from fastapi import FastAPI, Depends, HTTPException
from auth.login import login_router
from auth.registration import registration_router
from auth.password_reset import password_reset_router
from auth.verify import verify_router
from database.db import init_db



app = FastAPI()
app.include_router(login_router)
app.include_router(registration_router)
app.include_router(verify_router)
app.include_router(password_reset_router)


init_db()

@app.get("/")
async def home():
    return {"message": "Welcome to the FastAPI application!"}