from abc import ABC, abstractmethod
from typing import Optional
from app.models.user import User

class IUserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass
