from fastapi import FastAPI
from app.api.endpoints.zones import router as zones_router

# Crear la aplicación FastAPI
app = FastAPI(
    title="ms-ingestion",
    description="Microservicio de ingesta de datos territoriales",
    version="1.0.0",
)

# Registrar el router de zonas
# Esto "activa" los endpoints definidos en zones.py
app.include_router(zones_router)


@app.get("/")
def root():
    return {"message": "ms-ingestion is running", "version": "1.0.0"}
