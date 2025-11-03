from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database.models import User
from database.db import SessionLocal
from sqlalchemy.orm import Session

login_router = APIRouter(
    prefix="/login",
    tags=["login"],
)


class UserLogin(BaseModel):
    email: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


import hashlib
def hash_password_sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def verify_password_sha256(raw: str, hashed: str) -> bool:
    return hash_password_sha256(raw) == hashed


@login_router.post("/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    user_reqord = db.query(User).filter(User.email == user.email).first()
    if not user_reqord or not verify_password_sha256(user.password, user_reqord.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in.")
    return {"message": "User login route is working!"}