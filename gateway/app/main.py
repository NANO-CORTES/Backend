from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.endpoints import proxy
import uuid
import logging

logger = logging.getLogger("GatewayService")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [Trace: %(trace_id)s] - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

app = FastAPI(title="BFF API Gateway")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    adapter = logging.LoggerAdapter(logger, {'trace_id': trace_id})
    request.state.logger = adapter
    
    adapter.info(f"Gateway proxying request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        adapter.info(f"Gateway response status: {response.status_code}")
        return response
    except Exception as e:
        adapter.error(f"Gateway Internal Error: {e}")
        return JSONResponse(status_code=500, content={"error": "Gateway Error", "trace_id": trace_id})

app.include_router(proxy.router, prefix="/api/v1", tags=["proxy"])

@app.get("/health")
def health_check():
    import time
    return {
        "status": "healthy",
        "service_name": "bff-gateway",
        "version": "1.0.0",
        "db_connected": False,
        "timestamp": int(time.time())
    }
