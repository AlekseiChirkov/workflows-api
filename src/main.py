from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers.workflows import router as workflows_router
from src.api.routers.triggers import router as trigger_router
from src.core.logger import get_logger
from src.core.exceptions import AppException, app_exception_handler
from src.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    RequestSizeLimitMiddleware,
    RateLimitMiddleware
)
from src.core.request_context import get_request_id
from src.core.config import settings
from src.infrastructure.messaging.producer import PubSubProducer

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = PubSubProducer(
        project_id=settings.GCP_PROJECT_ID,
        topic_name=settings.PUBSUB_TOPIC_WORKFLOW_EVENTS,
    )

    app.state.event_producer = producer

    try:
        yield
    finally:
        producer.close()


def create_app() -> FastAPI:
    tags_metadata = [
        {
            "name": "workflows",
            "description": "Operations for managing business processes (workflows).",
        },
        {
            "name": "tasks",
            "description": "Managing tasks within a workflow.",
        },
        {
            "name": "triggers",
            "description": "Managing triggers that start a workflow.",
        },
        {
            "name": "auth",
            "description": "API Key authentication",
        },
    ]

    app = FastAPI(
        title="Workflow Automation API",
        version="1.0.0",
        description="""
        API for Workflow Automation platform.
        Allows creating and managing workflows, tasks and triggers.

        Main features:
        - Create workflows
        - Manage workflow tasks
        - Manage workflow triggers
        - Run workflows (coming soon)
        """,
        openapi_tags=tags_metadata,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://your-client.com"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestSizeLimitMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    app.include_router(workflows_router)
    app.include_router(trigger_router)
    app.add_exception_handler(AppException, app_exception_handler)

    return app


app = create_app()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        }
    }

    openapi_schema["security"] = [
        {"ApiKeyAuth": []},
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema



app.openapi = custom_openapi


@app.exception_handler(HTTPException)
async def http_exceptionhandler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "request_id": get_request_id(),
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        extra={
            "error": str(exc),
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "Internal Server Error",
            "request_id": get_request_id(),
        }
    )
