from pydantic import BaseModel
from typing import Optional

class EventCreate(BaseModel):
    # Les ponemos valores por defecto para que NUNCA den error 422
    user_id: Optional[str] = "system"
    action: Optional[str] = "unknown_action"
    service_name: Optional[str] = "frontend_web"
    status: Optional[str] = "info"
    details: Optional[str] = None

    class Config:
        from_attributes = True