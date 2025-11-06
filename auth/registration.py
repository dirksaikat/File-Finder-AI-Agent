from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
import re
from database.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from database.models import User, VerificationToken
from utils.mailer import send_verification_email
import hashlib
from utils.verify_code import make_code_and_hash

registration_router = APIRouter(
    prefix="/register",
    tags=["registration"],
)


class UserRegistration(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    terms_accepted: bool



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()


@registration_router.post("/")
def register(user: UserRegistration,bg: BackgroundTasks, db: Session = Depends(get_db)):
    required_fields = [user.name, user.email, user.password, user.confirm_password, user.terms_accepted]

    if not all(required_fields):
        raise HTTPException(status_code=400, detail="All fields are required.")
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", user.email):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    user_reqord = db.query(User).filter(User.email == user.email).first()
    if user_reqord:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", user.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    if not user.terms_accepted:
        raise HTTPException(status_code=400, detail="Terms must be accepted.")
    user_record = User(
            name=user.name,
            email=user.email,
            hashed_password=hash_password(user.password),
            terms_accepted=user.terms_accepted,
            is_verified=False,
        )
    db.add(user_record)
    db.flush()  # get user_record.id

    code, salt, digest, expires_at = make_code_and_hash(ttl_minutes=10)

    tok = VerificationToken(
        user_id=user_record.id,
        token=digest,
        purpose="verify_code",
        salt=salt,
        expires_at=expires_at,
    )
    db.add(tok)
    db.commit()

    body = f"Your verification code is: {code}\nIt expires in 10 minutes."
    bg.add_task(send_verification_email, user_record.email, "Your verification code", body)
    return {"message": "Registration successful. Please check your email to verify your account."}