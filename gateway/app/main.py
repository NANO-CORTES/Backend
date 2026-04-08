from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="BFF Gateway")

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MS_AUTH_URL = "http://ms-auth:8006"
MS_INGESTION_URL = "http://ms-ingestion:8001"


async def _proxy(request: Request, target_url: str) -> Response:
    """Forward a request to a downstream microservice."""
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


# ---------- Auth routes ----------
@app.post("/api/v1/auth/login")
async def proxy_login(request: Request):
    return await _proxy(request, f"{MS_AUTH_URL}/api/v1/auth/login")


# ---------- Admin user routes ----------
@app.post("/api/v1/admin/users")
async def proxy_create_user(request: Request):
    return await _proxy(request, f"{MS_AUTH_URL}/api/v1/admin/users")


@app.get("/api/v1/admin/users")
async def proxy_list_users(request: Request):
    return await _proxy(request, f"{MS_AUTH_URL}/api/v1/admin/users")


@app.put("/api/v1/admin/users/{user_id}")
async def proxy_update_user(user_id: str, request: Request):
    return await _proxy(request, f"{MS_AUTH_URL}/api/v1/admin/users/{user_id}")


@app.delete("/api/v1/admin/users/{user_id}")
async def proxy_delete_user(user_id: str, request: Request):
    return await _proxy(request, f"{MS_AUTH_URL}/api/v1/admin/users/{user_id}")


@app.post("/api/v1/admin/users/{user_id}/reset-password")
async def proxy_reset_password(user_id: str, request: Request):
    return await _proxy(
        request, f"{MS_AUTH_URL}/api/v1/admin/users/{user_id}/reset-password"
    )


# ---------- Ingestion routes ----------
@app.post("/api/v1/ingestion/upload")
async def proxy_upload(request: Request):
    return await _proxy(request, f"{MS_INGESTION_URL}/upload")


@app.get("/")
def root():
    return {"message": "BFF Gateway is running"}
