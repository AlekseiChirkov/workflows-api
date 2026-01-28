import time
import asyncio
import logging

from src.db.models import ExecutionLog

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession

from src.actions.base import BaseAction, ExecutionContext, ActionResult
from src.repositories.execution_log import ExecutionLogRepository
from src.core import metrics as worker_metrics

MAX_ATTEMPTS = 3


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
            "queued_to_dlq": result.queued_to_dlq,
            "last_error": result.error,
            "action_duration_ms": (result.duration * 1000) if result.duration is not None else None,
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

    async def check_attempts(
        self,
        log_entry: ExecutionLog,
        context: ExecutionContext,
        action: BaseAction,
    ) -> ActionResult | None:
        await self.log_repo.increment_attempts(log_entry)
        if log_entry.attempts > MAX_ATTEMPTS:
            logger.warning(
                "Max attempts exceeded; flagging for DLQ",
                extra={
                    "trace_id": context.trace_id,
                    "workflow_id": str(context.workflow.id),
                    "event_id": str(context.event.event_id),
                    "action": action.__class__.__name__,
                    "attempts": log_entry.attempts,
                },
            )
            result = ActionResult(
                status="failed",
                error="Max attempts exceeded",
                retryable=False,
                queued_to_dlq=True,
            )
            await self._persist_log(log_entry, result)
            return result
        return None

    def _update_retryable_and_queued_to_dlq(
            self, result: ActionResult,
            log_entry: ExecutionLog,
            context: ExecutionContext,
            action: BaseAction
    ) -> ActionResult:
        if result.retryable and log_entry.attempts >= MAX_ATTEMPTS:
            result.retryable = False
            result.queued_to_dlq = True
            logger.warning(
                "Action reached max attempts; queued to DLQ",
                extra={
                    "trace_id": context.trace_id,
                    "workflow_id": str(context.workflow.id),
                    "event_id": str(context.event.event_id),
                    "action": action.__class__.__name__,
                    "attempts": log_entry.attempts,
                },
            )
        else:
            result.queued_to_dlq = False
        return result

    async def execute(self, action: BaseAction, context: ExecutionContext, timeout: float = 10.0) -> ActionResult:
        start = time.perf_counter()

        payload = {
            "workflow_id": context.workflow.id,
            "event_id": context.event.event_id,
            "trace_id": context.trace_id,
            "action": action.__class__.__name__,
            "status": "pending",
            "retryable": False,
        }
        log_entry, is_new = await self.log_repo.create_pending(payload)
        if not is_new:
            if log_entry.queued_to_dlq or log_entry.status in {"success", "skipped"}:
                logger.info(
                    "Duplicate event detected",
                    extra={
                        "trace_id": context.trace_id,
                        "workflow_id": str(context.workflow.id),
                        "event_id": str(context.event.event_id),
                        "action": action.__class__.__name__,
                        "status": log_entry.status,
                        "queued_to_dlq": log_entry.queued_to_dlq,
                    },
                )
                return ActionResult(status="skipped")

            if log_entry.status == "pending":
                logger.info(
                    "Execution in progress; skipping duplicate delivery",
                    extra={
                        "trace_id": context.trace_id,
                        "workflow_id": str(context.workflow.id),
                        "event_id": str(context.event.event_id),
                        "action": action.__class__.__name__,
                        "status": log_entry.status,
                        "queued_to_dlq": log_entry.queued_to_dlq,
                    },
                )
                return ActionResult(status="skipped")

        worker_metrics.record_attempt(context.workflow.id)

        result = await self.check_attempts(log_entry, context, action)
        if result:
            worker_metrics.record_failure(context.workflow.id)
            if result.queued_to_dlq:
                worker_metrics.record_dlq(context.workflow.id)
            return result

        result = await self._run_action(action, context, timeout)
        result.duration = time.perf_counter() - start
        worker_metrics.record_duration(context.workflow.id, result.duration)
        result = self._update_retryable_and_queued_to_dlq(
            result, log_entry, context, action
        )

        if result.status == "success":
            worker_metrics.record_success(context.workflow.id)
        else:
            worker_metrics.record_failure(context.workflow.id)
            if result.queued_to_dlq:
                worker_metrics.record_dlq(context.workflow.id)

        logger.info(
            "Action result",
            extra={
                "trace_id": context.trace_id,
                "workflow_id": str(context.workflow.id),
                "action": action.__class__.__name__,
                "status": result.status,
                "retryable": result.retryable,
                "duration": result.duration,
                "attempts": log_entry.attempts,
                "queued_to_dlq": result.queued_to_dlq,
            },
        )
        await self._persist_log(log_entry, result)
        return result