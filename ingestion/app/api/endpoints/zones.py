from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.schemas.schema import ZoneListResponse
from app.services.zone_service import zone_service


# Router es como un "mini-app" que agrupa rutas relacionadas
router = APIRouter(prefix="/api/v1", tags=["Zonas"])


@router.get(
    "/zones",
    response_model=ZoneListResponse,
    summary="Consultar zonas disponibles",
    description="Retorna lista de zonas únicas cargadas. Soporta paginación y filtro por dataset.",
)
def get_zones(
    dataset_id: Optional[str] = Query(
        None,
        description="ID del dataset a filtrar. Si no se envía, retorna todas las zonas."
    ),
    limit: int = Query(
        50,
        ge=1,       # ge = greater or equal → mínimo 1
        le=200,     # le = less or equal → máximo 200
        description="Cuántas zonas devolver por página (máximo 200)"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Desde qué posición empezar (para paginación)"
    ),
):
    # Llamar al servicio para obtener los datos
    result = zone_service.get_zones(
        dataset_id=dataset_id,
        limit=limit,
        offset=offset,
    )

    # Si no hay zonas, retornar error 404
    if result["total"] == 0:
        raise HTTPException(
            status_code=404,
            detail="No hay datasets válidos cargados aún"
        )

    # Construir y retornar respuesta exitosa
    return ZoneListResponse(
        success=True,
        total=result["total"],
        limit=limit,
        offset=offset,
        data=result["zones"],
        error=None,
    )