from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.database import engine, Base
from app.api.endpoints import auth
from app.core.middleware import TraceIdMiddleware
from app.core.exceptions import global_exception_handler
from sqlalchemy import text

# Create DB Schema
with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS configuration"))
    con.commit()

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Configuration Service")

# Setup Rate Limiting handler
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup E2E Global Error Handler
app.add_exception_handler(Exception, global_exception_handler)

# Setup Trace ID Middleware
app.add_middleware(TraceIdMiddleware)

# Setup Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

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
        "service_name": "ms-configuration",
        "version": "1.0.0",
        "db_connected": db_connected,
        "timestamp": int(time.time())
    }
