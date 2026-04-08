from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.user import User, RoleEnum
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """Find a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Find a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session) -> list[User]:
    """Return all users ordered by creation date."""
    return db.query(User).order_by(User.created_at.desc()).all()


def create_user(
    db: Session, email: str, full_name: str, password: str, role: str = "USER"
) -> User:
    """Create a new user with hashed password."""
    user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        role=RoleEnum(role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verify credentials and update last_login. Returns user or None."""
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    # Update last_login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session, user: User, role: str | None = None, is_active: bool | None = None
) -> User:
    """Update user role and/or active status."""
    if role is not None:
        user.role = RoleEnum(role)
    if is_active is not None:
        user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, user: User, new_password: str) -> None:
    """Set a new hashed password for the user."""
    user.password_hash = hash_password(new_password)
    db.commit()
