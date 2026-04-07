from fastapi import FastAPI
from app.api.endpoints.auth import router as auth_router

app = FastAPI(
    title="ms-auth",
    description="Microservicio de autenticación con JWT",
    version="1.0.0",
)

# HU-10 - Autenticación
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "ms-auth is running", "version": "1.0.0"}