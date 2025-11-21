from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from utils.verify_code import verify_code_matches, VerifyCode
from database.schemas import VerifyEmail
from database.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from .service import AuthService

verify_router = APIRouter(prefix="/verify",tags=["verify"])



@verify_router.post("/send-code")
async def verify_code_send(payload: VerifyEmail,background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService()
    result = await auth_service.get_user_by_email(session,payload.email)
    user = result.scalars().first()
    if not user:
        raise HTTPException(400,"Email not exists")
    else:
       await auth_service.send_verification_code_email(session=session,user=user,background_tasks=background_tasks)
    return {"message": "Verification eamil send to your email"}


@verify_router.get("/resend-code")
async def verify_code_resend():
    pass


@verify_router.post("/confirm")
async def verify_code_confirm():
    pass



