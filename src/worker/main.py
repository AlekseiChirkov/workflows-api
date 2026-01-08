import logging

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI

from src.worker.routers.pubsub import router as pubsub_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Workflow worker",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.include_router(pubsub_router)
    return app


app = create_app()
