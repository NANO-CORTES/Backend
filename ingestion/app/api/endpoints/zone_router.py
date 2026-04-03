from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

# Importaciones de tu proyecto
from app.core.database import get_db
from app.schemas.zones import ZoneResponse
from app.models.dataset import DatasetLoad
from app.core.security import get_current_user
# Si tienes un servicio creado, lo usas aquí; si no, lo hacemos directo con la DB:

router = APIRouter()

@router.get("/zones", response_model=List[ZoneResponse])
def get_zones(
    skip: int = 0, 
    limit: int = 100, 
    dataset_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna la lista de zonas (municipios) cargadas en el sistema.
    Permite filtrar por un dataset_id específico.
    """
    # Iniciamos la consulta en la tabla de ingesta
    query = db.query(DatasetLoad.id, DatasetLoad.file_name) 

    # Si el usuario pide las zonas de un archivo específico
    if dataset_id:
        query = query.filter(DatasetLoad.id == dataset_id)

    results = query.offset(skip).limit(limit).all()

    # Mapeamos los resultados al formato del Schema (zone_code y zone_name)
    # Nota: Aquí usamos el ID como code y el nombre del archivo como ejemplo, 
    # pero Brandon luego lo conectará con la tabla de 'Zonas' real.
    return [
        {"zone_code": str(r.id), "zone_name": r.file_name} 
        for r in results
    ]

from typing import Optional

@router.get("/zonas")
def listar_zonas(db: Session = Depends(get_db), skip: int = 0, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Retorna zonas con paginación empresarial (HU-04)."""
    return db.query(ZoneModel).offset(skip).limit(limit).all()

@router.get("/datasets", response_model=List[dict])
def list_all_datasets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Muestra todos los archivos que se han subido.
    Añadido: Paginación y Filtrado por estado (HU-04)
    """
    query = db.query(DatasetLoad)
    
    if status is not None:
        query = query.filter(DatasetLoad.status == status)
        
    datasets = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": d.id,
            "file_name": d.file_name,
            "status": d.status,
            "total_records": getattr(d, 'record_count', 0),
            "valid": getattr(d, 'valid_record_count', 0),
            "invalid": getattr(d, 'invalid_record_count', 0),
            "date": d.uploaded_at
        } for d in datasets
    ]