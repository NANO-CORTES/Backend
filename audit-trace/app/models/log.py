from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime

class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = {'schema': 'audit'}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    action = Column(String)
    service_name = Column(String)
    status = Column(String)
    details = Column(String, nullable=True) 
    timestamp = Column(DateTime, default=datetime.utcnow)