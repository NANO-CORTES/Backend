from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Microservice"

    class Config:
        env_file = ".env"

settings = Settings()
