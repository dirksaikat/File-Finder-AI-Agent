# routers/verify.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from utils.verify_code import make_code_and_hash, verify_code_matches
from database.db import SessionLocal
from database.models import VerificationToken, User
from utils.mailer import send_verification_email



verify_router = APIRouter(prefix="/verify", tags=["verification"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@verify_router.get("")
def verify_email(token: str, db: Session = Depends(get_db)):
    tok = db.query(VerificationToken).filter(
        VerificationToken.token == token,
        VerificationToken.purpose == "verify"
    ).first()
    if not tok:
        raise HTTPException(status_code=400, detail="Invalid token.")

    if tok.used_at is not None:
        raise HTTPException(status_code=400, detail="Token already used.")

    if tok.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired. Please request a new verification email.")

    user = db.query(User).filter(User.id == tok.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found for token.")

    user.is_verified = True
    tok.used_at = datetime.utcnow()
    db.commit()
    return {"message": "Email verified successfully. You can now log in."}


# routers/verify.py
@verify_router.post("/resend")
def resend_verification(email: str, bg: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account with that email.")
    if user.is_verified:
        return {"message": "This account is already verified."}

    # throttle logic unchanged ...

    # create 6-digit code
    code, salt, digest, expires_at = make_code_and_hash(ttl_minutes=10)

    tok = VerificationToken(
        user_id=user.id,
        token=digest,            # store hash only
        purpose="verify_code",   # distinguish from link tokens
        salt=salt,               # add this column if you don't have it yet
        expires_at=expires_at,
    )
    db.add(tok)
    db.commit()

    body = f"Your verification code is: {code}\nIt expires in 10 minutes."
    bg.add_task(send_verification_email, user.email, "Your verification code", body)
    return {"message": "Verification code sent."}



class CodePayload(BaseModel):
    email: str
    code: str

@verify_router.post("/confirm")
def confirm_code(payload: CodePayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account with that email.")

    tok = (db.query(VerificationToken)
             .filter(VerificationToken.user_id == user.id,
                     VerificationToken.purpose == "verify_code")
             .order_by(VerificationToken.created_at.desc())
             .first())

    if not tok:
        raise HTTPException(status_code=400, detail="No active code. Please request a new one.")
    if tok.used_at is not None:
        raise HTTPException(status_code=400, detail="Code already used. Request a new one.")
    if tok.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expired. Request a new one.")

    if not verify_code_matches(payload.code, tok.salt, tok.token):
        # optional: increment tok.attempts and lock after N tries
        raise HTTPException(status_code=400, detail="Invalid code.")

    user.is_verified = True
    tok.used_at = datetime.utcnow()
    db.commit()
    return {"message": "Email verified successfully."}