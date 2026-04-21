from sqlalchemy.orm import Session
from app.models.scoring import ScoreExecution, ZoneScore

class ScoringRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_full_execution(self, execution: ScoreExecution, zone_scores: list[ZoneScore]):
        """Punto 4: Persistir ScoreExecution y ZoneScore en una sola transacción"""
        try:
            self.db.add(execution)
            self.db.add_all(zone_scores)
            self.db.commit()
            self.db.refresh(execution)
            return execution
        except Exception as e:
            self.db.rollback()
            raise e

    def get_results_by_execution(self, execution_id: str):
        """Punto 5: Consultar resultados por execution_id"""
        return self.db.query(ZoneScore).filter(ZoneScore.execution_id == execution_id).all()