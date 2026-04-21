from fastapi import FastAPI
<<<<<<< HEAD

app = FastAPI(title="Microservice API")

@app.get("/")
def root():
    return {"message": "Service is running"}
=======
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.endpoints.ranking import router as ranking_router
from app.api.endpoints.health import router as health_router

app = FastAPI(
    title=settings.service_name,
    description="Microservicio de analítica y scoring territorial",
    version=settings.service_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ranking_router)
app.include_router(health_router)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
def root():
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "docs": "/docs",
    }
>>>>>>> feature/mis-cambios
