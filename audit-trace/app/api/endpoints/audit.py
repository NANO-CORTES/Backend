from fastapi import APIRouter, Depends, Request
from app.api.deps import get_audit_service
from app.interfaces.audit_service import IAuditService
from app.schemas.audit import AuditLogCreate, AuditLogResponse

router = APIRouter()

@router.post("/", response_model=AuditLogResponse, status_code=201)
def create_audit_log(
    request: Request,
    log_in: AuditLogCreate,
    audit_service: IAuditService = Depends(get_audit_service)
):
    # Usar el trace_id inyectado por el middleware HU-06
    trace_id = getattr(request.state, "trace_id", "Unknown")
    
    saved_log = audit_service.log_action(trace_id=trace_id, log_in=log_in)
    return saved_log
