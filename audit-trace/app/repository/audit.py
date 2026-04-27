from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.audit import AuditLog
from app.interfaces.audit_repo import IAuditRepository

class AuditRepository(IAuditRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        try:
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
        except SQLAlchemyError as err:
            self.db.rollback()
            raise err
