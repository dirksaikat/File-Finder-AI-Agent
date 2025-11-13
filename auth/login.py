from fastapi import APIRouter, Depends, HTTPException, status, Response
from database.models import User
from utils.utils import create_access_token, decode_access_token
from database.db import get_session
from database.schemas import LoginSchema
from sqlalchemy.ext.asyncio import AsyncSession
from auth.service import AuthService

router = APIRouter(prefix="/login", tags=["auth"])

@router.post("/", status_code=status.HTTP_200_OK)
async def login_user(Login_data: LoginSchema, response: Response, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService()
    user = auth_service.authenticate_user(session, Login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    if not auth_service.user_is_verified(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not verified."
        )
    
    access_token = create_access_token(data={"sub": user.email})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        expires=1800,
        path="/",
        secure=True,
    )

    return {"user": user.email, "access_token": access_token, "token_type": "bearer"}

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(token: str = Depends(), session: AsyncSession = Depends(get_session)):
    payload = decode_access_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials."
        )
    auth_service = AuthService()
    user = auth_service.get_user_by_email(session, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user