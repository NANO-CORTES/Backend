import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DBAPIError
from app.models.log import AuditEvent
from app.repositories.log_repository import LogRepository
from app.schemas.log import EventCreate

logger = logging.getLogger(__name__)

class LogService:
    """SOLID: Business logic encapsulating DB resilience outside of route context"""
    def __init__(self, repo: LogRepository, db: Session):
        self.repo = repo
        self.db = db

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((OperationalError, DBAPIError))
    )
    def save_event_with_retries(self, event_data: EventCreate, trace_id: str):
        """Asynchronously attempts to commit Audit Event mitigating temporary DB downtime"""
        try:
            new_event = AuditEvent(
                user_id=event_data.user_id,
                action=event_data.action,
                service_name=event_data.service_name,
                status=event_data.status,
                details=event_data.details
                # If trace_id was on the model, it would go here.
            )
            self.repo.create(new_event)
            self.db.commit()
            logger.info(f"Audit event saved. Trace: {trace_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to persist audit log: {e}. Retrying...")
            raise e
