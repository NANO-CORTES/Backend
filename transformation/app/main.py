from fastapi import FastAPI
from app.api.endpoints import transform
from app.core.middleware import TraceIdMiddleware
from app.core.exceptions import global_exception_handler

app = FastAPI(title="Transformation Service")

app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(TraceIdMiddleware)

app.include_router(transform.router, prefix="/api/v1/transformation", tags=["transformation"])

@app.get("/health")
def health_check():
    import time
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False
        
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "service_name": "ms-transformation",
        "version": "1.0.0",
        "db_connected": db_connected,
        "timestamp": int(time.time())
    }
