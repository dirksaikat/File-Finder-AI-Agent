from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_verified: bool = Field(default=False)
    terms_accepted: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="user")
    password_reset_tokens: List["PasswordResetToken"] = Relationship(back_populates="user")


class VerificationToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str
    purpose: str
    salt: Optional[str] = None
    attempts: int = Field(default=0)
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="verification_tokens")


class PasswordResetToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str
    salt: Optional[str] = None
    attempts: int = Field(default=0)
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="password_reset_tokens")