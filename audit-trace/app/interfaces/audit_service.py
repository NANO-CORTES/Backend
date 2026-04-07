from abc import ABC, abstractmethod
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogCreate

class IAuditService(ABC):
    @abstractmethod
    def log_action(self, trace_id: str, log_in: AuditLogCreate) -> AuditLog:
        pass
