from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> User | None:
    """Busca un usuario por su correo electrónico."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: any) -> User | None:
    """Busca un usuario por su ID único de base de datos."""
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session) -> list[User]:
    """Retorna la lista de todos los usuarios, ordenados por fecha de creación descendente."""
    return db.query(User).order_by(User.created_at.desc()).all()

def create_user(
    db: Session, email: str, full_name: str, password: str, role: str = "USER"
) -> User:
    """
    Crea un nuevo usuario en el sistema.
    
    Lógica:
    1. Hashea la contraseña para no guardarla en texto plano.
    2. Asigna el rol correspondiente (ADMIN/USER).
    3. Persiste en la base de datos.
    """
    user = User(
        email=email,
        full_name=full_name,
        password_hash=get_password_hash(password),
        role=UserRole(role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Valida las credenciales de un usuario.
    Si son correctas, actualiza la fecha de 'last_login'.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None
    
    # Compara el hash de la base de datos con la contraseña ingresada
    if not verify_password(password, user.password_hash):
        return None
        
    # Registro del último acceso
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user

def update_user(
    db: Session, user: User, role: str | None = None, is_active: bool | None = None
) -> User:
    """Actualiza datos específicos de un usuario (rol o estado activo/inactivo)."""
    if role is not None:
        user.role = UserRole(role)
    if is_active is not None:
        user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user

def reset_user_password(db: Session, user: User, new_password: str) -> None:
    """Cambia la contraseña de un usuario por una nueva (previamente hasheada)."""
    user.password_hash = get_password_hash(new_password)
    db.commit()
