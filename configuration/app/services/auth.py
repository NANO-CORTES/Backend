from typing import Optional
from app.interfaces.auth_service import IAuthService
from app.interfaces.user_repo import IUserRepository
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import DomainException

class AuthService(IAuthService):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def register_user(self, user_in: UserCreate) -> User:
        existing = self.user_repo.get_by_username(user_in.username)
        if existing:
            raise DomainException("Username already registered", status_code=400)
            
        new_user = User(
            username=user_in.username,
            password_hash=get_password_hash(user_in.password),
            role=user_in.role
        )
        return self.user_repo.create(new_user)
