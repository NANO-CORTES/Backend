from abc import ABC, abstractmethod
from typing import Optional
from app.models.audit import AuditLog

class IAuditRepository(ABC):
    @abstractmethod
    def create(self, log: AuditLog) -> AuditLog:
        pass
