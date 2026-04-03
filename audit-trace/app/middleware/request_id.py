import uuid
import time
import logging
import contextvars
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

trace_id_var = contextvars.ContextVar("trace_id", default="system")

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id_var.get()
        return True

logging.basicConfig(level=logging.INFO)
for handler in logging.root.handlers:
    handler.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] [Trace-ID: %(trace_id)s] - %(name)s - %(message)s"))
    handler.addFilter(TraceIdFilter())

logger = logging.getLogger(__name__)

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        request.state.trace_id = trace_id
        
        token = trace_id_var.set(trace_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Trace-Id"] = trace_id
            process_time = time.time() - start_time
            logger.info(f"Path: {request.url.path} | Time: {process_time:.4f}s")
            return response
        finally:
            trace_id_var.reset(token)
