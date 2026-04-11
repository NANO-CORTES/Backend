from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# Esquema de seguridad utilizando Bearer Token (JWT)
security_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extrae y valida al usuario actual a partir del token JWT enviado en el header Authorization.
    
    Proceso:
    1. Obtiene las credenciales del esquema Bearer.
    2. Decodifica el token usando la clave secreta.
    3. Verifica que el 'sub' (sujeto) del token sea el email del usuario.
    4. Consulta en la base de datos si el usuario existe y está activo.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    # El campo 'sub' contiene el identificador único (email en este caso)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta identificador",
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o cuenta inactiva",
        )

    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia de seguridad para proteger rutas administrativas.
    
    Valida que el usuario obtenido por get_current_user tenga el rol 'ADMIN'.
    Soporta verificaciones tanto de objetos Enum como de strings planos para mayor robustez.
    """
    # Normalización del rol a string para evitar errores de comparación entre Tipos Python y DB
    role_str = str(current_user.role.value) if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if role_str != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado: se requiere rol ADMIN (tu rol actual es: {role_str})",
        )
    return current_user
