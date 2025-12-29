import time
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()

        logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None,
            },
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                "Unhandled error",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                },
            )
            raise

        duration_ms = int((time.time() - start_time) * 1000)
        status = response.status_code
        if status >= 500:
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": duration_ms,
                }
            )
        elif status >= 400:
            logger.warning(
                "Client error",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": duration_ms,
                }
            )
        else:
            logger.info(
                "Request.completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": duration_ms,
                },
            )

        return response
