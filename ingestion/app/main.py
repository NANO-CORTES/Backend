from fastapi import FastAPI
from app.api.endpoints.zones import router as zones_router
from app.api.endpoints.health import router as health_router

app = FastAPI(
    title="ms-ingestion",
    description="Microservicio de ingesta de datos territoriales",
    version="1.0.0",
)

# HU-04 - Zonas
app.include_router(zones_router)

# HU-08 - Health check
app.include_router(health_router)


@app.get("/")
def root():
    return {"message": "ms-ingestion is running", "version": "1.0.0"}