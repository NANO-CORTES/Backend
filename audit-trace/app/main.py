from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

# ============ MODELOS ============
from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ProcessTrace(Base):
    __tablename__ = "process_traces"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_load_id = Column(String(100), nullable=False, index=True)
    transformation_run_id = Column(String(100), nullable=True)
    score_execution_id = Column(String(100), nullable=True)
    event_type = Column(String(50), nullable=False)
    status = Column(String(20), default="success")
    parameters = Column(JSON, nullable=True)
    result_summary = Column(JSON, nullable=True)
    user_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============ BASE DE DATOS ============
DATABASE_URL = "sqlite:///./audit_trace.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ SCHEMAS ============
class TraceCreate(BaseModel):
    dataset_load_id: str
    transformation_run_id: Optional[str] = None
    score_execution_id: Optional[str] = None
    event_type: str
    status: str = "success"
    parameters: Optional[Dict[str, Any]] = None
    result_summary: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class TraceResponse(BaseModel):
    id: int
    dataset_load_id: str
    event_type: str
    status: str
    parameters: Optional[Dict[str, Any]]
    result_summary: Optional[Dict[str, Any]]
    created_at: datetime

# ============ FASTAPI APP ============
app = FastAPI(title="Audit Trace Service")

@app.get("/")
def root():
    return {"message": "Audit Trace Service running"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "audit-trace"}

# ============ ENDPOINTS ============
@app.post("/api/v1/audit/trace")
def create_trace(trace: TraceCreate, db: Session = Depends(get_db)):
    db_trace = ProcessTrace(
        dataset_load_id=trace.dataset_load_id,
        transformation_run_id=trace.transformation_run_id,
        score_execution_id=trace.score_execution_id,
        event_type=trace.event_type,
        status=trace.status,
        parameters=trace.parameters,
        result_summary=trace.result_summary,
        user_id=trace.user_id
    )
    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)
    return {"id": db_trace.id, "status": "created"}

@app.get("/api/v1/audit/trace/{dataset_load_id}")
def get_trace_chain(dataset_load_id: str, db: Session = Depends(get_db)):
    events = db.query(ProcessTrace).filter(
        ProcessTrace.dataset_load_id == dataset_load_id
    ).order_by(ProcessTrace.created_at).all()
    
    if not events:
        raise HTTPException(status_code=404, detail="No se encontraron eventos")
    
    timeline = {}
    for event in events:
        timeline[event.event_type] = {
            "status": event.status,
            "parameters": event.parameters,
            "result_summary": event.result_summary,
            "timestamp": event.created_at.isoformat()
        }
    
    return {
        "dataset_load_id": dataset_load_id,
        "events": events,
        "timeline": timeline
    }