from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from database.config import config
import random

ACCESS_TOKEN_EXPIRE = 30  # Token expiry time

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {}
    except jwt.InvalidTokenError:
        return {}
    




VERIFICATION_CODE_EXPIRE_MINUTES = 10  # code valid for 10 minutes

def generate_verification_code() -> str:
    """
    Generate a 6-digit code as string, e.g. "483920".
    """
    return f"{random.randint(100000, 999999)}"

def get_verification_expiry() -> datetime:
    """
    When the verification code should expire.
    """
    return datetime.utcnow() + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES)




