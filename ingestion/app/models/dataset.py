from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime

class DatasetLoad(Base):
    __tablename__ = "dataset_loads"
    __table_args__ = {'schema': 'ingestion'}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    file_name = Column(String)
    file_hash = Column(String, unique=True, index=True) # For Idempotency
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="UPLOADED")
    validation_version = Column(String, default="v1.0")
    transformation_version = Column(String, default="v1.0")