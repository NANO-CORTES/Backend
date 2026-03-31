from pydantic import BaseModel
from typing import Optional, List


# Esto representa UNA zona individual
class ZoneItem(BaseModel):
    zone_code: str    # ej: "BOG-001"
    zone_name: str    # ej: "chapinero"


# Esto representa la RESPUESTA COMPLETA que devuelve el endpoint
class ZoneListResponse(BaseModel):
    success: bool          # True si todo salió bien
    total: int             # cuántas zonas existen en total
    limit: int             # cuántas se piden por página
    offset: int            # desde cuál número empieza
    data: List[ZoneItem]   # la lista de zonas
    error: Optional[str]   # None si no hay error, mensaje si hay error