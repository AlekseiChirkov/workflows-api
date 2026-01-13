import pytest
from uuid import uuid4

from src.actions.base import BaseAction
from src.events.schema import EventEnvelope
from src.models.actions import ActionResult, ExecutionContext
from src.repositories.execution_log import ExecutionLogRepository
from src.worker.services.executor import Executor
from src.db.models import Workflow


class DummyAction(BaseAction):
    calls = 0

    async def run(self, context):
        type(self).calls += 1
        return ActionResult(status="success")


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