from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "ms-auth"
    version: str = "1.0.0"
    
    # Configuración JWT
    jwt_secret: str = "proyecto-analisis-territorial-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60       # access token dura 60 minutos
    jwt_refresh_expiration_days: int = 7    # refresh token dura 7 días

    class Config:
        env_file = ".env"


settings = Settings()