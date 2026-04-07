import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from app.core.config import settings
from typing import Optional

router = APIRouter()
client = httpx.AsyncClient()

async def forward_request(request: Request, destination_url: str):
    # Genera el Trace_id para enviarlo a los microservicios
    trace_id = getattr(request.state, "trace_id", "")
    
    headers = dict(request.headers)
    headers["x-trace-id"] = trace_id
    # Evitar problemas asincronos con host de fastapi VS el downstream
    if "host" in headers:
        del headers["host"]
        
    try:
        # Pasa el body como streaming
        proxy_req = client.build_request(
            method=request.method,
            url=destination_url,
            headers=headers,
            content=request.stream()
        )
        response = await client.send(proxy_req, stream=True)
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as exc:
        logger = getattr(request.state, "logger", None)
        if logger:
            logger.error(f"Downstream connection error: {exc}")
        raise HTTPException(status_code=502, detail="Bad Gateway: downstream service unreachable.")

@router.api_route("/configuration/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_configuration(request: Request, path: str):
    url = f"{settings.MS_CONFIGURATION_URL}/{path}"
    # Merge query params
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/ingestion/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_ingestion(request: Request, path: str):
    url = f"{settings.MS_INGESTION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/audit/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_audit(request: Request, path: str):
    url = f"{settings.MS_AUDIT_TRACE_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/transformation/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_transformation(request: Request, path: str):
    url = f"{settings.MS_TRANSFORMATION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_analytics(request: Request, path: str):
    url = f"{settings.MS_ANALYTICS_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)
