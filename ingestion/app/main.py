from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.endpoints import dataset
from app.core.middleware import TraceIdMiddleware
from app.core.exceptions import global_exception_handler
from sqlalchemy import text
import time

# Create schema and tables with retry logic to ensure DB is ready
max_retries = 5
retry_count = 0

while retry_count < max_retries:
    try:
        # Ensure the ingestion schema exists before creating tables.
        with engine.begin() as con:
            con.execute(text("CREATE SCHEMA IF NOT EXISTS ingestion"))

        # Try to add the optional department column without rolling back schema creation.
        try:
            with engine.begin() as con:
                con.execute(text("ALTER TABLE ingestion.dataset_zones ADD COLUMN IF NOT EXISTS department VARCHAR"))
        except Exception:
            # Table might not exist yet, create_all will handle it.
            pass

        break  # Success, exit retry loop
    except Exception as e:
        retry_count += 1
        if retry_count < max_retries:
            print(f"Error during schema setup (retry {retry_count}/{max_retries}): {e}")
            time.sleep(1)
        else:
            print(f"Failed to create schema after {max_retries} retries: {e}")

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating tables: {e}")

app = FastAPI(title="Ingestion Service")

# Manejo global de excepciones para respuestas consistentes en JSON
app.add_exception_handler(Exception, global_exception_handler)

# Middleware para inyectar X-Trace-Id en cada petición
app.add_middleware(TraceIdMiddleware)

# Registro de Rutas
app.include_router(dataset.router, prefix="/datasets", tags=["datasets"])

@app.get("/health")
def health_check():
    """Endpoint de salud del servicio de Ingestión."""
    import time
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False
        
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "service_name": "ms-ingestion",
        "version": "1.0.0",
        "db_connected": db_connected,
        "timestamp": int(time.time())
    }

@app.get("/")
def root():
    return {"message": "Ingestion service is running"}
