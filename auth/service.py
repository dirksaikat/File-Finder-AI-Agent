from database.models import User, VerificationToken, PasswordResetToken
from utils.utils import get_password_hash, verify_password
from database.schemas import UserCreateSchema, LoginSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc


class AuthService:
    async def get_user_by_email(self, session: AsyncSession, email: str) -> User | None:
        user = await session.execute(
            select(User).where(User.email == email)
        )
        return user
    
    def user_exists(self, session: AsyncSession, email: str) -> bool:
        user = self.get_user_by_email(session, email)
        return user is not None
    
    def create_user(self, session: AsyncSession, user_data: UserCreateSchema) -> User:
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            terms_accepted=user_data.terms_accepted,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    


    async def authenticate_user(self, session: AsyncSession, login_data: LoginSchema) -> User | None:
        user = await self.get_user_by_email(session, login_data.email)
        if user and verify_password(login_data.password, user.hashed_password):
            return user
        return None
    
    def user_is_verified(self, user: User) -> bool:
        return user.is_verified
    

    
