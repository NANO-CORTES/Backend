from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import List, Dict
from app.interfaces.analytics_service import IAnalyticsService
from app.services.analytics import AnalyticsService

def get_analytics_service() -> IAnalyticsService:
    return AnalyticsService()

router = APIRouter()

@router.get("/zones/{dataset_hash}", response_model=List[Dict[str, str]], status_code=200)
def get_territories(
    request: Request,
    dataset_hash: str,
    analytics: IAnalyticsService = Depends(get_analytics_service)
):
    logger = getattr(request.state, "logger", None)
    if logger:
        logger.info(f"Querying zones for dataset: {dataset_hash}")

    z = analytics.get_zones(dataset_hash)
    return z
