from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: str
    terms_accepted: bool
    is_verified: bool
    created_at: str

class VerificationTokenSchema(BaseModel):
    id: int
    user_id: int
    token: str
    purpose: str
    salt: str | None
    attempts: int
    expires_at: str
    used_at: str | None
    created_at: str

class PasswordResetTokenSchema(BaseModel):
    id: int
    user_id: int
    token: str
    salt: str | None
    attempts: int
    expires_at: str
    used_at: str | None
    created_at: str

class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str
    terms_accepted: bool

class LoginSchema(BaseModel):
    email: str
    password: str


class VerifyEmail(BaseModel):
    email: str