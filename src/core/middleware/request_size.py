from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint, BaseHTTPMiddleware


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_size: int = 1_000_000):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        content_length = request.headers.get("content-length")
        if content_length is not None:
            size = int(content_length)
            if size > self.max_body_size:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "RequestTooLarge",
                        "message": "Request body is too large",
                    }
                )

        return await call_next(request)