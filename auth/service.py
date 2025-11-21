from fastapi_mail import MessageSchema
from fastapi import BackgroundTasks
from database.models import User, VerificationToken
from utils.utils import get_password_hash, verify_password, generate_verification_code, get_verification_expiry
from database.schemas import UserCreateSchema, LoginSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from utils.mailer import fm


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
        result = await self.get_user_by_email(session, login_data.email)
        user = result.scalars().first()
        if user and verify_password(login_data.password, user.hashed_password):
            return user
        return None
    
    def user_is_verified(self, user: User) -> bool:
        return user.is_verified
    

    async def send_verification_code_email(
        self,
        session: AsyncSession,
        user: User,
        background_tasks: BackgroundTasks,
    ):
        """
        Generate a 6-digit code, save it to the user, and send via email.
        """

        # 1️⃣ Generate code + expiry
        code = generate_verification_code()
        expires_at = get_verification_expiry()

        token = VerificationToken(
            user_id= user.id,
            token=code,
            purpose="Verify Email",
            expires_at=expires_at
        )
        session.add(token)
        await session.commit()
        await session.refresh(token)

        # 3️⃣ Build email content
        body = f"Your verification code is: {code}\nThis code will expire in 10 minutes."

        message = MessageSchema(
            subject="Your verification code",
            recipients=[user.email],
            body=body,
            subtype="plain",
        )

        # 4️⃣ Send in background
        background_tasks.add_task(fm.send_message, message)
    

    
