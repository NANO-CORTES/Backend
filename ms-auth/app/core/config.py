import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "ms-auth"

    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "admin")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "territorial_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey12345")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
