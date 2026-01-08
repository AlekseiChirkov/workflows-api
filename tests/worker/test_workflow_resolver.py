from datetime import datetime, timezone

import pytest
from uuid import uuid4

from src.worker.services.workflow_resolver import WorkflowResolver
from src.core.exceptions import WorkflowNotFound, WorkflowAlreadyExists, WorkflowInactive
from src.events.schema import EventEnvelope


class FakeWorkflow:
    def __init__(self, id, is_active=True):
        self.id = id
        self.is_active = is_active


class FakeWorkflowRepository:
    def __init__(self, workflow=None):
        self.workflow = workflow

    async def get_by_id(self, workflow_id):
        return self.workflow


@pytest.fixture
def event():
    return EventEnvelope(
        event_id=uuid4(),
        event_type="workflow.triggered",
        version=1,
        timestamp=datetime.now(timezone.utc),
        source="api",
        payload={"workflow_id": str(uuid4())},
        trace_id="test",
    )


@pytest.mark.asyncio
async def test_resolver_workflow_not_found(event):
    resolver = WorkflowResolver(session=None)
    resolver._repo = FakeWorkflowRepository(workflow=None)

    with pytest.raises(WorkflowNotFound):
        await resolver.resolve(event)


@pytest.mark.asyncio
async def test_resolver_workflow_inactive(event):
    wf = FakeWorkflow(id=event.payload["workflow_id"], is_active=False)

    resolver = WorkflowResolver(session=None)
    resolver._repo = FakeWorkflowRepository(workflow=wf)

    with pytest.raises(WorkflowInactive):
        await resolver.resolve(event)


@pytest.mark.asyncio
async def test_resolver_ok(event):
    wf = FakeWorkflow(id=event.payload["workflow_id"], is_active=True)

    resolver = WorkflowResolver(session=None)
    resolver._repo = FakeWorkflowRepository(workflow=wf)

    workflow = await resolver.resolve(event)
    assert workflow.id == wf.id
