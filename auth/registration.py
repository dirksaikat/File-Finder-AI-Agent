from fastapi import APIRouter, Depends, HTTPException

registration_router = APIRouter(
    prefix="/register",
    tags=["registration"],
)

@registration_router.get("/")
def register_test():
    return {"message": "User registration route is working!"}