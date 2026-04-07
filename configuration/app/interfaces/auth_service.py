from abc import ABC, abstractmethod
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate

class IAuthService(ABC):
    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        pass

    @abstractmethod
    def register_user(self, user_in: UserCreate) -> User:
        pass
