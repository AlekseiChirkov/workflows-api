import time
import asyncio
import logging

from src.db.models import ExecutionLog

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.base import BaseAction, ExecutionContext, ActionResult
from src.repositories.execution_log import ExecutionLogRepository


class Executor:
    def __init__(self, session: AsyncSession, log_repo: ExecutionLogRepository):
        self.session = session
        self.log_repo = log_repo

    async def _persist_log(self, log: ExecutionLog, result: ActionResult) -> None:
        payload = {
            "status": result.status,
            "result": result.result,
            "error": result.error,
            "retryable": result.retryable,
            "duration": result.duration,
        }
        await self.log_repo.mark_finished(log, payload)

    async def _run_action(self, action: BaseAction, context: ExecutionContext, timeout: float):
        try:
            return await asyncio.wait_for(action.run(context), timeout=timeout)
        except asyncio.TimeoutError:
            return ActionResult(
                status="failed",
                error="Action timed out",
                retryable=True,
            )
        except Exception as e:
            return ActionResult(
                status="failed",
                error=str(e),
                retryable=False,
            )

    async def execute(self, action: BaseAction, context: ExecutionContext, timeout: float = 10.0) -> ActionResult:
        start = time.perf_counter()

        payload = {
            "workflow_id": context.workflow.id,
            "event_id": context.event.event_id,
            "action": action.__class__.__name__,
            "status": "pending",
            "retryable": False,
        }
        log_entry, is_new = await self.log_repo.create_pending(payload)
        if not is_new:
            logger.info(
                "Duplicate event detected",
                extra={
                    "trace_id": context.trace_id,
                    "workflow_id": str(context.workflow.id),
                    "event_id": str(context.event.event_id),
                    "action": action.__class__.__name__,
                    "status": "skipped",
                }
            )
            return ActionResult(status="skipped")

        result = await self._run_action(action, context, timeout)
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
        await self._persist_log(log_entry, result)
        return result