from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
)
# Modelos de validación específicos para las peticiones administrativas
from pydantic import BaseModel
from typing import Optional

class ResetPasswordRequest(BaseModel):
    new_password: str

class MessageResponse(BaseModel):
    message: str

from app.services.user_service import (
    get_user_by_email,
    get_user_by_id,
    get_all_users,
    create_user,
    update_user,
    reset_user_password,
)

# Definición del Router con prefijo /admin/users
router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    request: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Permite a un administrador crear un nuevo usuario manualmente.
    Requiere que el email no esté registrado previamente.
    Protegido por: require_admin
    """
    existing = get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    user = create_user(
        db,
        email=request.email,
        full_name=request.full_name,
        password=request.password,
        role=request.role,
    )
    return user

@router.get("", response_model=list[UserResponse])
def admin_list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Retorna la lista completa de usuarios del sistema.
    Solo visible para administradores.
    """
    return get_all_users(db)

@router.put("/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: str,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Actualiza el rol o el estado (activar/desactivar) de un usuario específico.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    updated = update_user(db, user, role=request.role, is_active=request.is_active)
    return updated

@router.delete("/{user_id}", response_model=MessageResponse)
def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Desactiva a un usuario del sistema (Soft Delete).
    Seguridad: Un administrador no puede desactivarse a sí mismo.
    """
    if str(current_admin.id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta administradora",
        )

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # Simplemente lo marcamos como inactivo
    update_user(db, user, is_active=False)
    return MessageResponse(message="Usuario desactivado correctamente")

@router.post("/{user_id}/reset-password", response_model=MessageResponse)
def admin_reset_password(
    user_id: str,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Permite al administrador resetear la contraseña de cualquier usuario.
    Útil en casos de olvido o bloqueos de cuenta.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    reset_user_password(db, user, request.new_password)
    return MessageResponse(message="Contraseña restablecida correctamente")
