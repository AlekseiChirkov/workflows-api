from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.request_context import get_request_id


class AppException(Exception):
    """Base class for app-level exceptions."""
    pass


class WorkflowNotFound(AppException):
    pass


class WorkflowAlreadyExists(AppException):
    pass


def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc) or "Application error occurred",
            "request_id": get_request_id(),
        }
    )
