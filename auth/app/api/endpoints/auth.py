from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from app.schemas.schema import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["HU-10 - Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Recibe email y contraseña, retorna tokens JWT si las credenciales son correctas.",
)
def login(body: LoginRequest):
    """
    ✓ Verifica credenciales con bcrypt
    ✓ Retorna access_token (60 min) y refresh_token (7 días)
    ✓ Retorna 401 si credenciales incorrectas
    ✓ Contraseña nunca se guarda en texto plano
    """
    result = auth_service.login(
        email=body.email,
        password=body.password,
    )

    if "error" in result:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas",
        )

    return TokenResponse(**result)


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="Invalida el token JWT para que no pueda usarse más.",
)
def logout(authorization: Optional[str] = Header(None)):
    """
    Invalida el token en lista negra
    Retorna 401 si no se envía token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token no proporcionado",
        )

    token = authorization.replace("Bearer ", "")
    auth_service.logout(token)

    return {"message": "Sesión cerrada exitosamente"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    description="Retorna los datos del usuario autenticado a partir del JWT.",
)
def get_me(authorization: Optional[str] = Header(None)):
    """
    ✓ Decodifica el token y retorna datos del usuario
    ✓ Retorna 401 si el token es inválido o expirado
    ✓ Retorna 401 si el token fue invalidado por logout
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token no proporcionado",
        )

    token = authorization.replace("Bearer ", "")
    user = auth_service.get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado",
        )

    return user