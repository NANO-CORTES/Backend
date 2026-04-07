from abc import ABC, abstractmethod

class ITransformationService(ABC):
    @abstractmethod
    def transform_dataset(self, file_hash: str) -> str:
        pass
