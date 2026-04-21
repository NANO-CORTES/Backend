from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScoringRequest(BaseModel):
    transformation_run_id: str
    configuration_id: str

class ZoneScoreResponse(BaseModel):
    zone_id: str
    score_value: float
    score_level: str
    rank_position: Optional[int]

class ScoringResultResponse(BaseModel):
    execution_id: str
    transformation_run_id: str
    results: List[ZoneScoreResponse]

