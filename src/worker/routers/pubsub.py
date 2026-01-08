import logging

logger = logging.getLogger(__name__)

from uuid import uuid4

from fastapi import APIRouter, Response, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.log import LogAction
from src.db.session import get_session
from src.core.exceptions import WorkflowResolutionError
from src.models.actions import ExecutionContext
from src.repositories.execution_log import ExecutionLogRepository
from src.worker.services.executor import Executor
from src.worker.services.workflow_resolver import WorkflowResolver
from src.worker.models.pubsub_push import PubSubPushBody
from src.worker.services.pubsub_decoder import decode_pubsub_message

router = APIRouter(
    prefix="/worker",
    tags=["worker"]
)


@router.get("/health", status_code=status.HTTP_200_OK)
async def healthcheck():
    return {"status": "ok"}


@router.post("/pubsub/push")
async def pubsub_push(body: PubSubPushBody, session: AsyncSession = Depends(get_session)):
    logger.info("Received PubSub Push message", extra={})
    try:
        event = decode_pubsub_message(body)
        logger.info(
            "Worker handling event",
            extra={
                "trace_id": event.trace_id,
                "event_id": str(event.event_id),
                "workflow_id": str(event.workflow.id)
            }
        )
        resolver = WorkflowResolver(session)
        workflow = await resolver.resolve(event)
        executor = Executor(session, ExecutionLogRepository(session))
        context = ExecutionContext(
            event=event,
            workflow=workflow,
            trace_id=event.trace_id or str(uuid4())
        )
        action = LogAction()
        result = await executor.execute(action, context)
        if result.retryable:
            raise WorkflowResolutionError("Action failed with retryable error")
    except WorkflowResolutionError:
        logger.error("Workflow resolution error", exc_info=True)
        return Response(status_code=status.HTTP_200_OK)
    except ValueError:
        logger.error("Value error", exc_info=True)
        return Response(status_code=status.HTTP_200_OK)
    except Exception:
        logger.error("Unexpected error", exc_info=True)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info(
        "Resolved workflow",
        extra={
            "workflow_id": str(workflow.id),
            "event_id": str(event.event_id),
        },
    )
    return Response(status_code=status.HTTP_200_OK)
