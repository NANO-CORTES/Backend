from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ---------- Auth ----------
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    full_name: str


# ---------- Admin: Create user ----------
class CreateUserRequest(BaseModel):
    email: str
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(default="USER", pattern="^(ADMIN|USER)$")


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Admin: Update user ----------
class UpdateUserRequest(BaseModel):
    role: Optional[str] = Field(default=None, pattern="^(ADMIN|USER)$")
    is_active: Optional[bool] = None


# ---------- Admin: Reset password ----------
class ResetPasswordRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


# ---------- Generic ----------
class MessageResponse(BaseModel):
    message: str
