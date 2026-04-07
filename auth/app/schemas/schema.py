from pydantic import BaseModel, EmailStr
from typing import Optional


# Lo que el usuario envía para hacer login
class LoginRequest(BaseModel):
    email: EmailStr    # valida que sea un email
    password: str


# Lo que retorna el login exitoso
class TokenResponse(BaseModel):
    access_token: str     # token de 60 minutos
    refresh_token: str    # token de 7 días
    token_type: str       # siempre "bearer"


# Lo que retorna el endpoint /me
class UserResponse(BaseModel):
    email: str
    full_name: str
    role: str             # "ADMIN" o "USER"
    is_active: bool