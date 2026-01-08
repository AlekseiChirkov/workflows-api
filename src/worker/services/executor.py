import time
import asyncio
import logging

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.base import BaseAction, ExecutionContext, ActionResult
from src.repositories.execution_log import ExecutionLogRepository


class Executor:
    def __init__(self, session: AsyncSession, log_repo: ExecutionLogRepository):
        self.session = session
        self.log_repo = log_repo

    async def _persist_log(self, action: BaseAction, context: ExecutionContext, result: ActionResult) -> None:
        payload = {
            "workflow_id": context.workflow.id,
            "event_id": context.event.event_id,
            "action": action.__class__.__name__,
            "status": result.status,
            "result": result.result,
            "error": result.error,
            "retryable": result.retryable,
            "duration": result.duration,
        }
        await self.log_repo.create(payload)

    async def execute(self, action: BaseAction, context: ExecutionContext, timeout: float = 10.0) -> ActionResult:
        start = time.perf_counter()

        try:
            result = await asyncio.wait_for(action.run(context), timeout=timeout)
        except asyncio.TimeoutError:
            result = ActionResult(
                status="failed",
                error="Action timed out",
                retryable=True,
            )
        except Exception as e:
            result = ActionResult(
                status="failed",
                error=str(e),
                retryable=False,
            )
        finally:
            result.duration = time.perf_counter() - start
            logger.info(
                "Action result",
                extra={
                    "trace_id": context.trace_id,
                    "workflow_id": str(context.workflow.id),
                    "action": action.__class__.__name__,
                    "status": result.status,
                    "retryable": result.retryable,
                    "duration": result.duration,
                },
            )
            await self._persist_log(action, context, result)
        return result