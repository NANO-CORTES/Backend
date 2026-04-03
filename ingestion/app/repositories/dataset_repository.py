from sqlalchemy.orm import Session
from app.models.dataset import DatasetLoad

class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_hash(self, file_hash: str):
        return self.db.query(DatasetLoad).filter(DatasetLoad.file_hash == file_hash).first()

    def create(self, dataset: DatasetLoad) -> DatasetLoad:
        self.db.add(dataset)
        return dataset # Defer commit to the service transactional block