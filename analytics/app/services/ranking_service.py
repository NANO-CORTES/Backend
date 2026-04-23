from typing import Optional
from app.interfaces.ranking_repository import IRankingRepository
from app.schemas.schema import RankingResponse, ZoneRankingItem, ScoreLevel

PAGE_SIZE = 20


class RankingService:
    #- SRP: solo maneja lógica de ranking, no acceso a BD ni HTTP.
    #- DIP: depende de IRankingRepository (abstracción), no de la implementación.
    #- OCP: para cambiar la fuente de datos, se inyecta otro repositorio.

    def __init__(self, repository: IRankingRepository):
        # Inyección de dependencia — DIP
        self._repository = repository

    def get_ranking(
        self,
        execution_id: str,
        level: Optional[str],
        page: int,
        page_size: int,
    ) -> RankingResponse:
        """
        Retorna el ranking paginado de zonas.
        Usa datos reales si existen, mock si no hay scoring previo.
        """
        self._validate_level(level)
        self._validate_pagination(page, page_size)

        offset = (page - 1) * page_size

        # Strategy: intentar datos reales primero
        execution = self._repository.get_execution(execution_id)

        if execution:
            zones_raw, total = self._repository.get_by_execution(
                execution_id, level, page_size, offset
            )
            items = [self._to_item_from_model(z) for z in zones_raw]
        else:
            # Fallback a mock si no hay ejecución real (HU-15 pendiente)
            zones_raw, total = self._repository.get_mock_data(
                execution_id, level, page_size, offset
            )
            items = [self._to_item_from_dict(z) for z in zones_raw]

        total_pages = max(1, -(-total // page_size))  # ceil division

        return RankingResponse(
            success=True,
            execution_id=execution_id,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            level_filter=level,
            data=items,
        )

    # Métodos privados

    def _validate_level(self, level: Optional[str]):
        """OCP: validación separada, fácil de extender."""
        valid_levels = {e.value for e in ScoreLevel}
        if level and level.upper() not in valid_levels:
            raise ValueError(
                f"Nivel '{level}' inválido. Valores permitidos: {sorted(valid_levels)}"
            )

    def _validate_pagination(self, page: int, page_size: int):
        if page < 1:
            raise ValueError("El número de página debe ser mayor a 0.")
        if page_size < 1 or page_size > 100:
            raise ValueError("El tamaño de página debe estar entre 1 y 100.")

    def _to_item_from_model(self, zone) -> ZoneRankingItem:
        """Convierte modelo SQLAlchemy a schema Pydantic."""
        return ZoneRankingItem(
            rank_position=zone.rank_position,
            zone_code=zone.zone_code,
            zone_name=zone.zone_name,
            score_value=round(zone.score_value, 4),
            score_level=zone.score_level,
            execution_id=zone.execution_id,
        )

    def _to_item_from_dict(self, zone: dict) -> ZoneRankingItem:
        """Convierte dict mock a schema Pydantic."""
        return ZoneRankingItem(
            rank_position=zone["rank_position"],
            zone_code=zone["zone_code"],
            zone_name=zone["zone_name"],
            score_value=round(zone["score_value"], 4),
            score_level=ScoreLevel(zone["score_level"]),
            execution_id=zone["execution_id"],
        )