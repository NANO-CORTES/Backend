from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_auth_service
from app.interfaces.auth_service import IAuthService
from app.schemas.user import Token, UserCreate, UserResponse
from app.core.security import create_access_token, require_role
from app.core.exceptions import DomainException

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute") # HU-10 Rate limiting (5 intentos por minuto)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: IAuthService = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
def register(
    user_in: UserCreate, 
    auth_service: IAuthService = Depends(get_auth_service)
):
    return auth_service.register_user(user_in)

# Ejemplo de endpoint protegido con validación multicapa (HU-11)
@router.get("/me", response_model=dict)
def read_users_me(
    request: Request,
    current_user: dict = Depends(require_role(["ADMIN", "USER"]))
):
    return {
        "username": current_user.get("sub"),
        "role": current_user.get("role"),
        "trace_id": request.state.trace_id
    }
