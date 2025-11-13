from fastapi import APIRouter, Depends

verify_router = APIRouter(prefix="/verify",tags=["verify"])