from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    project_name: str = "Microservice"

    service_name: str = "ms-analytics"
    service_version: str = "1.0.0"
    service_port: int = 8005
    environment: str = "dev"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/territorial_db"


    class Config:
        env_file = ".env"


settings = Settings()

settings = Settings()

