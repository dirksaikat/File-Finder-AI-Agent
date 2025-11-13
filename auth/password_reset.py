from fastapi import APIRouter, Depends, HTTPException
from database.db import get_session
from database.models import PasswordResetToken


password_reset_router = APIRouter(prefix="/password_reset", tags=["password_reset"])