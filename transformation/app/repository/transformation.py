from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.transformation import TransformationRun
from typing import List

class TransformationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, run: TransformationRun) -> TransformationRun:
        try:
            self.db.add(run)
            self.db.commit()
            self.db.refresh(run)
            return run
        except SQLAlchemyError as err:
            self.db.rollback()
            raise err

    def get_all(self, limit: int = 100, skip: int = 0) -> List[TransformationRun]:
        return self.db.query(TransformationRun).order_by(TransformationRun.processed_at.desc()).offset(skip).limit(limit).all()

    def get_by_user(self, user_id: str, limit: int = 100, skip: int = 0) -> List[TransformationRun]:
        return self.db.query(TransformationRun).filter(TransformationRun.user_id == user_id).order_by(TransformationRun.processed_at.desc()).offset(skip).limit(limit).all()
