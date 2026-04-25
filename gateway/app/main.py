from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.api.endpoints import proxy
from fastapi.middleware.cors import CORSMiddleware
from app.core.auth_middleware import auth_middleware
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
    
    if request.url.path.endswith("/health"):
        adapter.info(f"Health check request received for {request.url.path}")
    else:
        adapter.info(f"Gateway proxying request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        if not request.url.path.endswith("/health"):
            adapter.info(f"Gateway response status: {response.status_code}")
        return response
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail, "trace_id": trace_id})
    except Exception as e:
        adapter.error(f"Gateway Internal Error: {e}")
        return JSONResponse(status_code=500, content={"error": "Gateway Error", "trace_id": trace_id})

# Auth Middleware (must be after CORS but effectively wraps other controllers)
@app.middleware("http")
async def wrap_auth_middleware(request: Request, call_next):
    return await auth_middleware(request, call_next)

# Add CORS last so it is the OUTERMOST middleware (called first for requests).
# In FastAPI/Starlette, middlewares are executed in reverse order of addition.
# Current Stack: CORSMiddleware -> wrap_auth_middleware -> add_process_time_header -> Router
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://[::1]:5173",
        "http://[::1]:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proxy.router, prefix="/api/v1", tags=["proxy"])

@app.get("/api/bff/compare")
async def compare_zones(
    zones: str = Query(..., description="Códigos de zonas separados por coma. Ej: ZC1,ZC2,ZC3")
):
    from typing import List, Dict
    import httpx
    from fastapi import Query, HTTPException

    zone_list: List[str] = [z.strip() for z in zones.split(",") if z.strip()]

    if len(zone_list) < 2 or len(zone_list) > 5:
        raise HTTPException(status_code=400, detail="Debe seleccionar entre 2 y 5 zonas")

    comparison_data: Dict[str, dict] = {}
    max_values: Dict[str, float] = {}

    async with httpx.AsyncClient(timeout=10.0) as client:
        for zone_code in zone_list:
            try:
                response = await client.get(
                    f"http://analytics:8000/api/v1/zone-summary/{zone_code}"
                )
                response.raise_for_status()
                data = response.json()

                comparison_data[zone_code] = {
                    "zone_name": data.get("zone_name", zone_code),
                    "population_indicator": data.get("population_indicator"),
                    "income_indicator": data.get("income_indicator"),
                    "education_indicator": data.get("education_indicator"),
                    "competition_indicator": data.get("competition_indicator"),
                    "score": data.get("score") or data.get("combined_score")
                }
            except Exception:
                comparison_data[zone_code] = {"error": "No se pudieron obtener datos"}

    indicators = ["population_indicator", "income_indicator", "education_indicator", 
                  "competition_indicator", "score"]

    for ind in indicators:
        values = [comparison_data[z].get(ind) for z in zone_list 
                  if isinstance(comparison_data[z].get(ind), (int, float))]
        if values:
            max_values[ind] = max(values)

    return {
        "zones": zone_list,
        "comparison": comparison_data,
        "max_values": max_values,
        "indicators": indicators
    }

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