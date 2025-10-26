from fastapi import FastAPI, Depends, HTTPException
from auth.login import login_router
from auth.registration import registration_router


app = FastAPI()
app.include_router(login_router)
app.include_router(registration_router)



@app.get("/")
async def home():
    return {"message": "Welcome to the FastAPI application!"}