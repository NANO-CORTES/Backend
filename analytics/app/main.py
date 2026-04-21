from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints.scoring import router as scoring_router # HU-15
from app.api.endpoints.ranking import router as ranking_router
from app.api.endpoints.health import router as health_router
from app.core.config import settings
from app.core.database import init_db


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
app.include_router(scoring_router, prefix="/scoring", tags=["Scoring"]) # HU-15


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