from uuid import uuid4

import pytest
import pytest_asyncio

from src.repositories.execution_log import ExecutionLogRepository


@pytest_asyncio.fixture
async def repo(async_session):
    return ExecutionLogRepository(async_session)


@pytest_asyncio.fixture
async def payload(active_workflow):
    return {
        "workflow_id": active_workflow.id,
        "event_id": uuid4(),
        "action": "Dummy",
        "status": "pending",
        "retryable": False,
    }


@pytest.mark.asyncio
async def test_create_pending_duplicate(repo, payload):
    log, is_new = await repo.create_pending(payload)
    assert is_new is True

    dup, is_new_dup = await repo.create_pending(payload)
    assert is_new_dup is False
    assert dup.id == log.id