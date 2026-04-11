import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from app.core.config import settings
from typing import Optional

router = APIRouter()
client = httpx.AsyncClient()

async def forward_request(request: Request, destination_url: str):
    """
    Función Genérica de Proxy (Pasarela).
    Toma una petición recibida por el Gateway y la reenvía al microservicio correspondiente.
    """
    trace_id = getattr(request.state, "trace_id", "")
    
    # Preparamos los headers, preservando el trace_id para trazabilidad
    headers = dict(request.headers)
    headers["x-trace-id"] = trace_id
    
    # Eliminamos el header 'host' para evitar conflictos de ruteo en el microservicio destino
    if "host" in headers:
        del headers["host"]
        
    try:
        # Construimos la petición de salida apuntando al microservicio
        proxy_req = client.build_request(
            method=request.method,
            url=destination_url,
            headers=headers,
            content=request.stream()
        )
        # Enviamos la petición y devolvemos la respuesta en streaming (eficiente para archivos grandes)
        response = await client.send(proxy_req, stream=True)
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as exc:
        # Manejo de errores de conexión (ej. si un microservicio está caído)
        import logging
        logging.getLogger("GatewayProxy").error(f"Error conectando a {destination_url}: {exc}")
        raise HTTPException(
            status_code=502, 
            detail=f"Bad Gateway: El microservicio en {destination_url} no responde."
        )

# --- MAPEO DE RUTAS (PROXY) ---

@router.api_route("/configuration/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_configuration(request: Request, path: str):
    """Redirige peticiones al Microservicio de Configuración."""
    url = f"{settings.MS_CONFIGURATION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/ingestion/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_ingestion(request: Request, path: str):
    """Redirige peticiones al Microservicio de Ingestión."""
    url = f"{settings.MS_INGESTION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/audit/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_audit(request: Request, path: str):
    """Redirige peticiones al Microservicio de Auditoría."""
    url = f"{settings.MS_AUDIT_TRACE_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/transformation/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_transformation(request: Request, path: str):
    """Redirige peticiones al Microservicio de Transformación."""
    url = f"{settings.MS_TRANSFORMATION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_analytics(request: Request, path: str):
    """Redirige peticiones al Microservicio de Analítica."""
    url = f"{settings.MS_ANALYTICS_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_auth(request: Request, path: str):
    """Redirige peticiones al Microservicio de Autenticación (Login/Registro)."""
    url = f"{settings.MS_AUTH_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/admin/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_admin(request: Request, path: str):
    """
    Ruta especial para Administración.
    Envía las peticiones al Microservicio de Auth, pero bajo el prefijo /admin/ para segregación.
    """
    url = f"{settings.MS_AUTH_URL}/admin/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)
