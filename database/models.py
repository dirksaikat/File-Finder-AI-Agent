# database/models.py
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
import secrets
from datetime import datetime, timedelta
from database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    terms_accepted = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    tokens = relationship("VerificationToken", back_populates="user", cascade="all, delete-orphan")

    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="tokens")
    token = Column(String(128), unique=True, index=True, nullable=False)  # stores SHA-256 hex (64 chars)
    purpose = Column(String(32), default="verify", nullable=False)
    salt = Column(String(64), nullable=True)          # <-- add this for code flow
    attempts = Column(Integer, default=0, nullable=False)  # <-- optional
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user = relationship("User", back_populates="password_reset_tokens")
    token = Column(String(128), unique=True, index=True, nullable=False)  # stores SHA-256 hex (64 chars)
    salt = Column(String(64), nullable=True)          # <-- add this for code flow
    attempts = Column(Integer, default=0, nullable=False)  # <-- optional
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)