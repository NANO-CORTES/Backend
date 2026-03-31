from typing import Optional, List
from app.schemas.schema import ZoneItem


# Por ahora usamos datos de prueba (mock)
# Cuando tus compañeros conecten la BD, esto cambia aquí
# sin tocar el endpoint
_MOCK_ZONES = [
    {"zone_code": "BOG-001", "zone_name": "chapinero"},
    {"zone_code": "BOG-002", "zone_name": "suba"},
    {"zone_code": "BOG-003", "zone_name": "usaquen"},
    {"zone_code": "BOG-004", "zone_name": "kennedy"},
    {"zone_code": "BOG-005", "zone_name": "engativa"},
    {"zone_code": "BOG-006", "zone_name": "bosa"},
]


class ZoneService:
    """
    Contiene toda la lógica relacionada con zonas.
    Principio SRP: esta clase solo hace cosas de zonas.
    """

    def get_zones(
        self,
        dataset_id: Optional[str],
        limit: int,
        offset: int,
    ) -> dict:
        """
        Retorna zonas disponibles con paginación.
        dataset_id: si se envía, filtraría por ese dataset (simulado por ahora)
        limit: cuántas zonas devolver máximo
        offset: desde cuál zona empezar
        """
        # Obtener todas las zonas disponibles
        all_zones = self._fetch_zones(dataset_id)

        # Calcular total antes de paginar
        total = len(all_zones)

        # Aplicar paginación: cortar la lista
        # Ejemplo: offset=0, limit=3 → zonas 0,1,2
        # Ejemplo: offset=3, limit=3 → zonas 3,4,5
        paginated = all_zones[offset : offset + limit]

        # Convertir a objetos ZoneItem
        zone_items = [ZoneItem(**z) for z in paginated]

        return {
            "total": total,
            "zones": zone_items,
        }

    def _fetch_zones(self, dataset_id: Optional[str]) -> list:
        """
        Método privado (el _ al inicio indica que es interno).
        Aquí iría la consulta a la BD.
        Por ahora retorna datos de prueba.
        """
        # Cuando haya BD real, esto sería algo como:
        # return db.query(Zone).filter(Zone.dataset_id == dataset_id).all()
        return _MOCK_ZONES


# Instancia única del servicio (patrón Singleton simple)
zone_service = ZoneService()