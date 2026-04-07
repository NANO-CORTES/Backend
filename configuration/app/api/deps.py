from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.repository.user import UserRepository
from app.services.auth import AuthService
from app.interfaces.user_repo import IUserRepository
from app.interfaces.auth_service import IAuthService

def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)

def get_auth_service(user_repo: IUserRepository = Depends(get_user_repository)) -> IAuthService:
    return AuthService(user_repo)
