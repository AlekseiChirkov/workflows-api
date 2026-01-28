import asyncio

import pytest
from types import SimpleNamespace
from uuid import uuid4

from src.actions.base import BaseAction
from src.events.schema import EventEnvelope
from src.models.actions import ActionResult, ExecutionContext
from src.repositories.execution_log import ExecutionLogRepository
from src.worker.services.executor import Executor, MAX_ATTEMPTS
from src.db.models import Workflow


class DummyAction(BaseAction):
    calls = 0

    async def run(self, context):
        type(self).calls += 1
        return ActionResult(status="success")



class SlowAction(BaseAction):
    def __init__(self, delay: float):
        self.delay = delay

    async def run(self, context):
        await asyncio.sleep(self.delay)
        return ActionResult(status="success")


class RetryableAction(BaseAction):
    async def run(self, context):
        return ActionResult(status="failed", error="boom", retryable=True)


@pytest.mark.asyncio
async def test_executor_skips_duplicates(async_session, envelope):
    workflow = Workflow(
        id=uuid4(),
        name=f"test-workflow-{uuid4()}",
        description="test workflow",
        status="published",
        is_active=True,
    )
    async_session.add(workflow)
    await async_session.flush()

    repo = ExecutionLogRepository(async_session)
    executor = Executor(async_session, repo)
    context = ExecutionContext(
        event=EventEnvelope(**envelope),
        workflow=workflow,
        trace_id="test-trace",
    )

    DummyAction.calls = 0
    action = DummyAction()

    first = await executor.execute(action, context)
    second = await executor.execute(action, context)

    assert first.status == "success"
    assert second.status == "skipped"
    assert DummyAction.calls == 1

    logs = await repo.list(workflow_id=workflow.id)
    assert len(logs) == 1, "Created duplicated logs"
    assert logs[0].event_id == context.event.event_id
    assert logs[0].status == "success"


@pytest.mark.asyncio
async def test_executor_check_attempts_flags_dlq(async_session, envelope):
    workflow = Workflow(
        id=uuid4(),
        name=f"test-workflow-{uuid4()}",
        description="test workflow",
        status="published",
        is_active=True,
    )
    async_session.add(workflow)
    await async_session.flush()

    repo = ExecutionLogRepository(async_session)
    executor = Executor(async_session, repo)
    context = ExecutionContext(
        event=EventEnvelope(**envelope),
        workflow=workflow,
        trace_id="test-trace",
    )

    payload = {
        "workflow_id": workflow.id,
        "event_id": context.event.event_id,
        "action": RetryableAction.__name__,
        "status": "pending",
        "retryable": False,
        "trace_id": context.trace_id,
        "payload_snapshot": context.event.payload,
    }
    log_entry, _ = await repo.create_pending(payload)
    log_entry.attempts = MAX_ATTEMPTS
    await async_session.flush()

    result = await executor.check_attempts(log_entry, context, RetryableAction())

    assert result is not None
    assert result.status == "failed"
    assert result.retryable is False
    assert result.queued_to_dlq is True


@pytest.mark.asyncio
async def test_update_retryable_marks_dlq(async_session):
    repo = ExecutionLogRepository(async_session)
    executor = Executor(async_session, repo)
    context = SimpleNamespace(
        trace_id="trace",
        workflow=SimpleNamespace(id=uuid4()),
        event=SimpleNamespace(event_id=uuid4()),
    )
    log_entry = SimpleNamespace(attempts=MAX_ATTEMPTS)
    action = DummyAction()

    result = ActionResult(status="failed", error="boom", retryable=True)
    updated = executor._update_retryable_and_queued_to_dlq(result, log_entry, context, action)

    assert updated.retryable is False
    assert updated.queued_to_dlq is True


@pytest.mark.asyncio
async def test_executor_timeout_moves_to_dlq(async_session, envelope):
    workflow = Workflow(
        id=uuid4(),
        name=f"timeout-workflow-{uuid4()}",
        description="timeout workflow",
        status="published",
        is_active=True,
    )
    async_session.add(workflow)
    await async_session.flush()

    repo = ExecutionLogRepository(async_session)
    executor = Executor(async_session, repo)
    context = ExecutionContext(
        event=EventEnvelope(**envelope),
        workflow=workflow,
        trace_id="timeout-trace",
    )

    action = SlowAction(delay=0.2)
    timeout = 0.05

    for attempt in range(MAX_ATTEMPTS - 1):
        result = await executor.execute(action, context, timeout=timeout)
        assert result.status == "failed"
        assert result.retryable is True
        assert result.queued_to_dlq is False

    final_result = await executor.execute(action, context, timeout=timeout)
    assert final_result.status == "failed"
    assert final_result.retryable is False
    assert final_result.queued_to_dlq is True

    logs = await repo.list(event_id=context.event.event_id)
    assert len(logs) == 1
    log = logs[0]
    assert log.status == "failed"
    assert log.queued_to_dlq is True
    assert log.attempts == MAX_ATTEMPTS
