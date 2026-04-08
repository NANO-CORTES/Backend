from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.schemas.user import LoginRequest, TokenResponse
from app.services.user_service import authenticate_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = authenticate_user(db, request.email, request.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada. Contacte al administrador.",
        )

    token_data = {"sub": user.id, "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.value,
        full_name=user.full_name,
    )
