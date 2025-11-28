import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from utils.verify_code import VerifyCode
from database.schemas import SendCode , VerifyEmail
from database.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from .service import AuthService
from database.models import VerificationToken
from sqlmodel import select
verify_router = APIRouter(prefix="/verify",tags=["verify"])



@verify_router.post("/send-code")
async def verify_code_send(payload: SendCode,background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService()
    result = await auth_service.get_user_by_email(session,payload.email)
    user = result.scalars().first()
    if not user:
        raise HTTPException(400,"Email not exists")
    else:
       await auth_service.send_verification_code_email(session=session,user=user,background_tasks=background_tasks)
    return {"message": "Verification email sent to your email"}


@verify_router.get("/resend-code")
async def verify_code_resend(payload: SendCode,background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService()
    result = await auth_service.get_user_by_email(session,payload.email)
    user = result.scalars().first()
    if not user:
        raise HTTPException(400,"Email not exists")
    else:
       await auth_service.send_verification_code_email(session=session,user=user,background_tasks=background_tasks)
    return {"message": "Verification email resent to your email"}


@verify_router.post("/confirm")
async def verify_code_confirm(payload: VerifyEmail, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService()
    result = await auth_service.get_user_by_email(session,payload.email)
    user = result.scalars().first()
    if not user:
        raise HTTPException(400,"Email not exists")
    token_result = await session.execute(
        select(VerificationToken).where(
            VerificationToken.user_id == user.id
        )
    )
    token_entry = token_result.scalars().first()
    if not token_entry:
        raise HTTPException(400,"No verification code found. Please request a new code.")
    if token_entry.expires_at > datetime.datetime.utcnow():
        raise HTTPException(400,"Verification code has expired. Please request a new code.")
    user.is_verified = True
    session.delete(token_entry)  # Remove used token
    await session.commit()
    return {"message": "Email successfully verified."}