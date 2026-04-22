from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt

from app.core.config import settings
from app.schemas.schema import UserResponse


# Usuarios de prueba — cuando haya BD real esto viene de PostgreSQL
_FAKE_USERS = {
    "admin@test.com": {
        "password_hash": bcrypt.hashpw(b"admin123", bcrypt.gensalt()),
        "role": "ADMIN",
        "full_name": "Admin Usuario",
        "is_active": True,
    },
    "user@test.com": {
        "password_hash": bcrypt.hashpw(b"user123", bcrypt.gensalt()),
        "role": "USER",
        "full_name": "Usuario Normal",
        "is_active": True,
    },
}

# Tokens invalidados por logout
# En producción esto va en Redis o en tabla BD
_TOKEN_BLACKLIST: set = set()


class AuthService:

    def login(self, email: str, password: str) -> dict:
    
        # Paso 1: buscar usuario
        user = _FAKE_USERS.get(email)

        # Paso 2: verificar que existe y está activo
        if not user or not user["is_active"]:
            return {"error": "Credenciales inválidas"}

        # Paso 3: verificar contraseña con bcrypt
        password_correct = bcrypt.checkpw(
            password.encode(),
            user["password_hash"]
        )

        if not password_correct:
            return {"error": "Credenciales inválidas"}

        # Paso 4: generar tokens
        access_token = self._create_token(
            email=email,
            role=user["role"],
            expires_in=timedelta(minutes=settings.jwt_expiration_minutes),
        )

        refresh_token = self._create_token(
            email=email,
            role=user["role"],
            expires_in=timedelta(days=settings.jwt_refresh_expiration_days),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def logout(self, token: str) -> bool:
        """
        Invalida el token agregándolo a la lista negra.
        """
        _TOKEN_BLACKLIST.add(token)
        return True

    def get_current_user(self, token: str) -> Optional[UserResponse]:
        """
        Decodifica el token y retorna los datos del usuario.
        """
        # Verificar si el token fue invalidado por logout
        if token in _TOKEN_BLACKLIST:
            return None

        try:
            # Decodificar el token JWT
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )

            email = payload.get("sub")
            user = _FAKE_USERS.get(email)

            if not user:
                return None

            return UserResponse(
                email=email,
                full_name=user["full_name"],
                role=user["role"],
                is_active=user["is_active"],
            )

        except jwt.ExpiredSignatureError:
            return None    # token expirado
        except jwt.InvalidTokenError:
            return None    # token inválido

    def _create_token(self, email: str, role: str, expires_in: timedelta) -> str:
        """
        Método privado — crea un token JWT con los datos del usuario.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": email,          # subject: email del usuario
            "role": role,          # rol para autorización
            "iat": now,            # issued at: cuándo se creó
            "exp": now + expires_in,  # expiration: cuándo expira
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


auth_service = AuthService()