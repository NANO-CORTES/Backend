from fastapi import FastAPI
from app.api.endpoints import zones
from app.core.middleware import TraceIdMiddleware
from app.core.exceptions import global_exception_handler

app = FastAPI(title="Analytics Service")

app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(TraceIdMiddleware)

app.include_router(zones.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/health")
def health_check():
    import time
    db_connected = False
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        db_connected = True
    except ImportError:
        pass
    except Exception:
        db_connected = False

    return {
        "status": "healthy" if db_connected else "unhealthy",
        "service_name": "ms-analytics",
        "version": "1.0.0",
        "db_connected": db_connected,
        "timestamp": int(time.time())
    }
