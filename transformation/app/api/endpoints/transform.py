from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.interfaces.transformation_service import ITransformationService
from app.services.transformer import TransformationService
from app.repository.transformation import TransformationRepository
from app.schemas.transformation import TransformationRunResponse

class TransformRequest(BaseModel):
    file_hash: str
    user_id: Optional[str] = None

class TransformResponse(BaseModel):
    file_hash: str
    status: str
    processed_file_path: Optional[str] = None

def get_transformation_service(db: Session = Depends(get_db)) -> ITransformationService:
    repo = TransformationRepository(db)
    return TransformationService(repo)

router = APIRouter()

@router.post("/", response_model=TransformResponse, status_code=200)
def process_transform(
    request: Request,
    payload: TransformRequest,
    transform_service: ITransformationService = Depends(get_transformation_service)
):
    logger = getattr(request.state, "logger", None)
    if logger:
        logger.info(f"Starting transformation for {payload.file_hash}")

    output_path = transform_service.transform_dataset(payload.file_hash, user_id=payload.user_id)
    
    if logger:
        logger.info(f"Transformation done -> {output_path}")

    return {
        "file_hash": payload.file_hash,
        "status": "COMPLETED",
        "processed_file_path": output_path
    }

@router.get("/results", response_model=List[TransformationRunResponse])
def get_transformation_results(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    transform_service: ITransformationService = Depends(get_transformation_service)
):
    return transform_service.get_results(limit=limit, skip=skip)
