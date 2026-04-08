from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.schemas.user import (
    CreateUserRequest,
    UserResponse,
    UpdateUserRequest,
    ResetPasswordRequest,
    MessageResponse,
)
from app.services.user_service import (
    get_user_by_email,
    get_user_by_id,
    get_all_users,
    create_user,
    update_user,
    reset_user_password,
)

router = APIRouter(prefix="/api/v1/admin/users", tags=["Admin - Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Create a new user. Email must be unique."""
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
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.get("", response_model=list[UserResponse])
def admin_list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """List all users in the system."""
    users = get_all_users(db)
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role.value,
            is_active=u.is_active,
            created_at=u.created_at,
            last_login=u.last_login,
        )
        for u in users
    ]


@router.put("/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: str,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Update a user's role and/or active status."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    updated = update_user(db, user, role=request.role, is_active=request.is_active)
    return UserResponse(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        role=updated.role.value,
        is_active=updated.is_active,
        created_at=updated.created_at,
        last_login=updated.last_login,
    )


@router.delete("/{user_id}", response_model=MessageResponse)
def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Soft-delete a user (set is_active=false). Admin cannot deactivate themselves."""
    if current_admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta",
        )

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    update_user(db, user, is_active=False)
    return MessageResponse(message="Usuario desactivado correctamente")


@router.post("/{user_id}/reset-password", response_model=MessageResponse)
def admin_reset_password(
    user_id: str,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Reset a user's password to a new temporary password."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    reset_user_password(db, user, request.new_password)
    return MessageResponse(message="Contraseña restablecida correctamente")
