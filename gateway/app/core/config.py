from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "API Gateway"
    MS_CONFIGURATION_URL: str = "http://ms_configuration:8003"
    MS_INGESTION_URL: str = "http://ms_ingestion:8001"
    MS_AUDIT_TRACE_URL: str = "http://ms_audit-trace:8002"
    MS_TRANSFORMATION_URL: str = "http://ms_transformation:8004"
    MS_ANALYTICS_URL: str = "http://ms_analytics:8005"

settings = Settings()
