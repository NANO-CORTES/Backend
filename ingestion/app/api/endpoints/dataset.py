from fastapi import APIRouter, Depends, File, Request, UploadFile, Query, HTTPException
from typing import List, Optional

from app.api.deps import getIngestionService
from app.core.security import get_current_user
from app.interfaces.ingestionService import IIngestionService
from app.interfaces.datasetRepo import IDatasetRepository
from app.schemas.dataset import DatasetResponse, ZoneListResponse
from app.api.deps import getDatasetRepository

router = APIRouter()


@router.post("/upload", response_model=DatasetResponse)
async def uploadDataset(
    request: Request,
    file: UploadFile = File(...),
    currentUser: dict = Depends(get_current_user),
    ingestionService: IIngestionService = Depends(getIngestionService)
):
    dataset = await ingestionService.processUpload(
        userId=currentUser["username"],
        file=file
    )

    logger = getattr(request.state, "logger", None)
    if logger:
        logger.info(
            f"Dataset '{dataset.fileName}' (id={dataset.datasetId}, "
            f"size={dataset.fileSize}B) cargado por '{currentUser['username']}' "
            f"— hash: {dataset.fileHash}"
        )

    return dataset


@router.get("/", response_model=List[DatasetResponse])
def getDatasets(
    datasetRepo: IDatasetRepository = Depends(getDatasetRepository)
):
    return datasetRepo.getAll()


@router.get("/zones", response_model=ZoneListResponse)
def getZones(
    datasetId: Optional[str] = Query(None, description="Filtrar por datasetId"),
    search: Optional[str] = Query(None, description="Buscar por nombre o código"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    datasetRepo: IDatasetRepository = Depends(getDatasetRepository)
):
    zones, total = datasetRepo.getZones(datasetId=datasetId, search=search, limit=limit, offset=offset)
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {"zoneCode": z.zoneCode, "zoneName": z.zoneName} for z in zones
        ]
    }


@router.get("/{id}", response_model=DatasetResponse)
def getDatasetById(
    id: str,
    datasetRepo: IDatasetRepository = Depends(getDatasetRepository)
):
    dataset = datasetRepo.getById(id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return dataset
