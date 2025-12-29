from uuid import uuid4

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import RequestResponseEndpoint, BaseHTTPMiddleware

from src.core.request_context import set_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get("X-Request-ID")
        request_id = incoming or str(uuid4())

        set_request_id(request_id)

        response = await call_next(request)

        response.headers["X-Request-Id"] = request_id
        return response