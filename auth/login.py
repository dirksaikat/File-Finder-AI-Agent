from fastapi import APIRouter, Depends, HTTPException

login_router = APIRouter(
    prefix="/login",
    tags=["login"],
)


@login_router.get("/")
def login_test():
    return {"message": "User login route is working!"}