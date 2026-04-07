from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class TransformationRun(Base):
    __tablename__ = "transformation_runs"

    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, index=True)
    status = Column(String)
    total_rows = Column(Integer)
    processed_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True) # To be connected later with real users
    details = Column(JSON, nullable=True) # Summary stats or errors
