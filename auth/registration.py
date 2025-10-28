from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import re
from database.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from database.models import User

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


import hashlib
def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

@registration_router.post("/")
def register(user: UserRegistration, db: Session = Depends(get_db)):
    required_fields = [user.name, user.email, user.password, user.confirm_password, user.terms_accepted]

    if not all(required_fields):
        raise HTTPException(status_code=400, detail="All fields are required.")
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", user.email):
        raise HTTPException(status_code=400, detail="Invalid email format.")
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
        terms_accepted=user.terms_accepted
    )
    db.add(user_record)
    db.commit()

    
    return {"message": "User registration route is working!"}