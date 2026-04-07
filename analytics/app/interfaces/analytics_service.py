from abc import ABC, abstractmethod
from typing import List, Dict

class IAnalyticsService(ABC):
    @abstractmethod
    def get_zones(self, dataset_hash: str) -> List[Dict[str, str]]:
        pass
