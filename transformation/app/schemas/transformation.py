from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class TransformationRunBase(BaseModel):
    file_hash: str
    status: str
    total_rows: int
    user_id: Optional[str] = None

class TransformationRunCreate(TransformationRunBase):
    pass

class TransformationRunResponse(TransformationRunBase):
    id: int
    processed_at: datetime
    details: Optional[dict] = None

    class Config:
        from_attributes = True

class TransformationResult(BaseModel):
    id: int
    file_hash: str
    status: str
    processed_at: datetime
    total_rows: int
    summary: Optional[dict] = None
