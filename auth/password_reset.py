from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from utils.verify_code import make_code_and_hash, verify_code_matches
from utils.mailer import send_password_reset_email
from database.db import SessionLocal
from database.models import PasswordResetToken, User


password_reset_router = APIRouter(prefix="/password-reset", tags=["password-reset"])


class PasswordResetRequest(BaseModel):
    email: str


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


@password_reset_router.post("/request")
def request_password_reset(payload: PasswordResetRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account with that email.")

    code, salt, digest, expires_at = make_code_and_hash(ttl_minutes=15)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=digest,          # <-- was: code
        salt=salt,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    bg.add_task(send_password_reset_email, user.email, code)
    return {"message": "Password reset email sent if the account exists."}


class PasswordResetConfirm(BaseModel):
    email: str
    code: str
    new_password: str

@password_reset_router.post("/confirm")
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found.")

    reset_token = (
        db.query(PasswordResetToken)
          .filter(
              PasswordResetToken.user_id == user.id,
              PasswordResetToken.used_at.is_(None),
              PasswordResetToken.expires_at > datetime.utcnow(),
          )
          .order_by(PasswordResetToken.expires_at.desc())
          .first()
    )

    if not reset_token:  # <-- was: if not reset_token.token
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    if not verify_code_matches(payload.code, reset_token.salt, reset_token.token):
        raise HTTPException(status_code=400, detail="Invalid code.")

    user.hashed_password = hash_password_sha256(payload.new_password)
    reset_token.used_at = datetime.utcnow()
    db.commit()
    return {"message": "Password has been reset successfully."}
