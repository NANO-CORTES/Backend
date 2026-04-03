from fastapi import FastAPI, Depends, UploadFile, File, Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import httpx
import time
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.api.endpoints.zone_router import router as zones_router

# Importaciones de tu core y servicios
from app.core.database import engine, Base, get_db
from app.core.security import get_current_user
from app.repositories.dataset_repository import DatasetRepository
from app.services.dataset_service import DatasetService
from app.core.file_security import FileSecurityValidator
from app.middleware.request_id import RequestIdMiddleware

logger = logging.getLogger(__name__)

# Asegurar esquema y tablas al arrancar
from sqlalchemy import text
with engine.connect() as con:
    try:
        con.execute(text("CREATE SCHEMA IF NOT EXISTS ingestion"))
        con.commit()
    except Exception as e:
        logger.warning(f"No se pudo crear el esquema: {e}")

Base.metadata.create_all(bind=engine)

# Configuración de Seguridad y Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8003/login")

app = FastAPI(title="Ingestion Service")
app.add_middleware(RequestIdMiddleware)

# --- CONFIGURACIÓN DE CORS CORREGIDA ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Tu Frontend de React/Vite
        "http://127.0.0.1:5173",    # Alternativa local
        "http://localhost:8001",    # El propio Swagger de Ingestión
    ],
    allow_credentials=True,         
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NUEVO: REGISTRO DE LAS RUTAS DE ZONAS Y DATASETS ---
# Esto hace que las rutas que me pasaste funcionen bajo /api/v1/datasets
# app.include_router(zones_router, prefix="/api/v1/datasets", tags=["Datasets y Zonas"])
# -------------------------------------------------------

# --- RESILIENCIA DE AUDITORÍA (HU-09) ---
@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
async def _do_send_audit_event(user_id: str, action: str, trace_id: str, status: str, details: str):
    async with httpx.AsyncClient() as client:
        payload = {
            "user_id": user_id,
            "action": action,
            "service_name": "ms-ingestion",
            "status": status,
            "details": details,
            "timestamp": time.time() 
        }
        headers = {"X-Trace-Id": trace_id}
        resp = await client.post("http://ms_audit-trace:8002/api/v1/audit/logs", json=payload, headers=headers)
        resp.raise_for_status()

async def send_audit_event(user_id: str, action: str, trace_id: str, status: str = "SUCCESS", details: str = None):
    try:
        await _do_send_audit_event(user_id, action, trace_id, status, details)
    except Exception as e:
        logger.error(f"Fallo crítico en Auditoría para rastro {trace_id}: {e}")

# --- DEPENDENCIAS ---
def get_dataset_service(db: Session = Depends(get_db)):
    repo = DatasetRepository(db)
    return DatasetService(repo=repo, db=db)

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    return {"status": "healthy", "service_name": "ms-ingestion"}

@app.post("/api/v1/datasets/upload")
async def upload_dataset(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service)
):
    # 1. VALIDACIÓN HU-01: FORMATOS PERMITIDOS
    allowed_extensions = ["csv", "json"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Extensión .{file_ext} no permitida. Solo se admite: {', '.join(allowed_extensions)}"
        )

    trace_id = getattr(request.state, 'trace_id', "unknown")
    username = current_user.get("username", "unknown") if current_user else "unknown"
    
    try:
        # 2. SEGURIDAD OWASP: Sanitización y Hash
        safe_filename = FileSecurityValidator.sanitize_filename(file.filename)
        file_hash, file_content = await FileSecurityValidator.validate_and_hash(file)

        # 3. LÓGICA DE NEGOCIO: Persistencia
        result_data = service.process_and_store_dataset(
            username=username,
            original_filename=safe_filename,
            file_content=file_content,
            file_hash=file_hash
        )
        
        # 4. AUDITORÍA ASÍNCRONA (HU-09)
        background_tasks.add_task(send_audit_event, username, "DATASET_UPLOAD", trace_id, "SUCCESS", f"Archivo: {safe_filename}")
            
        return {
            "success": True,
            "data": result_data
        }

    except Exception as e:
        error_msg = str(e.detail) if hasattr(e, 'detail') else str(e)
        background_tasks.add_task(send_audit_event, username, "DATASET_UPLOAD", trace_id, "FAILED", error_msg)
        logger.error(f"Error en upload: {error_msg}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Fallo interno en el procesamiento del archivo.")