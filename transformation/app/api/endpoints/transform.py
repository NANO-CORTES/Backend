from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional
from app.interfaces.transformation_service import ITransformationService
from app.services.transformer import TransformationService

class TransformRequest(BaseModel):
    file_hash: str

class TransformResponse(BaseModel):
    file_hash: str
    status: str
    processed_file_path: Optional[str] = None

def get_transformation_service() -> ITransformationService:
    return TransformationService()

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

    output_path = transform_service.transform_dataset(payload.file_hash)
    
    if logger:
        logger.info(f"Transformation done -> {output_path}")

    return {
        "file_hash": payload.file_hash,
        "status": "COMPLETED",
        "processed_file_path": output_path
    }
