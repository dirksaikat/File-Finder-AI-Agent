from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from database.models import User
from database.db import SessionLocal
from sqlalchemy.orm import Session
import hashlib
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta

login_router = APIRouter(
    prefix="/login",
    tags=["login"],
)


SECRET_KEY = "6cnQ3EgO_VxtQ32zV7OmiDAZWEoCW2rW2_0M9y9DAaY"
ALGORITHM = "HS256"

class UserLogin(BaseModel):
    email: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password_sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def verify_password_sha256(raw: str, hashed: str) -> bool:
    return hash_password_sha256(raw) == hashed


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




@login_router.post("/")
def login(user: UserLogin,response: Response, db: Session = Depends(get_db)):
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    user_reqord = db.query(User).filter(User.email == user.email).first()
    print(user_reqord.is_verified if user_reqord else "No user found")
    if not user_reqord or not verify_password_sha256(user.password, user_reqord.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if user_reqord.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in.")
    access = create_access_token(data={"sub": user_reqord.email})
    
    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        secure=False,          # True in HTTPS
        samesite="Lax",        # "None" (+ Secure) if cross-site
        max_age=15*60,
        path="/"
    )
    
    return {"user": {"id": user_reqord.id, "email": user_reqord.email}}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@login_router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user