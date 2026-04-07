from abc import ABC, abstractmethod
from typing import List
from app.models.transformation import TransformationRun

class ITransformationService(ABC):
    @abstractmethod
    def transform_dataset(self, file_hash: str, user_id: str = None) -> str:
        pass

    @abstractmethod
    def get_results(self, limit: int = 100, skip: int = 0) -> List[TransformationRun]:
        pass
