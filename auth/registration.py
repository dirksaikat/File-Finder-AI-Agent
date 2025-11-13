from fastapi import APIRouter, Depends, HTTPException, status
from database.models import User
from utils.utils import get_password_hash, verify_password, create_access_token, decode_access_token
from database.db import get_session
from database.schemas import UserCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


register_router = APIRouter(prefix="/register", tags=["auth"])


@register_router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    existing_user = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        terms_accepted=user_data.terms_accepted,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return {"message": "User registered successfully."}
