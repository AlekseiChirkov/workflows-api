import base64
import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import status
from sqlalchemy.exc import OperationalError

from src.core.exceptions import WorkflowNotFound
from src.models.actions import ActionResult
from src.repositories.execution_log import ExecutionLogRepository
from tests.conftest import async_session


def make_push_payload(envelope: dict):
    return {
        "message": {
            "messageId": "1",
            "data": base64.b64encode(
                json.dumps(envelope).encode()
            ).decode(),
            "attributes": {},
            "publishTime": datetime.now(timezone.utc).isoformat(),
        },
        "subscription": "projects/test/subscriptions/test",
    }


@pytest.mark.asyncio
async def test_worker_ack_on_business_error(client, envelope):
    payload = make_push_payload(envelope)

    response = await client.post(
        "/worker/pubsub/push",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_worker_retry_on_infra_error(client, monkeypatch, envelope):
    async def broken_resolve(*args, **kwargs):
        raise Exception("DB down")

    monkeypatch.setattr(
        "src.worker.services.workflow_resolver.WorkflowResolver.resolve",
        broken_resolve,
    )

    payload = make_push_payload(envelope)

    response = await client.post(
        "/worker/pubsub/push",
        json=payload,
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_worker_fatal_on_workflow_not_found(client, monkeypatch, envelope, async_session):
    async def broken_resolve(*_):
        raise WorkflowNotFound("missing")
    monkeypatch.setattr(
        "src.worker.services.workflow_resolver.WorkflowResolver.resolve",
        broken_resolve,
    )
    payload = make_push_payload(envelope)
    response = await client.post("/worker/pubsub/push", json=payload)
    assert response.status_code == status.HTTP_200_OK

    repo = ExecutionLogRepository(async_session)
    logs = await repo.list(event_id=envelope["event_id"])

    assert len(logs) == 0, "WorkflowNotFound shouldn't create execution logs"


@pytest.mark.asyncio
async def test_worker_returns_200_when_queued_to_dlq(client, monkeypatch, envelope):
    async def fake_session():
        class DummySession:
            async def close(self):
                pass

        yield DummySession()

    async def fake_execute(*_, **__):
        return ActionResult(status="failed", queued_to_dlq=True)

    async def fake_resolve(*_, **__):
        return type("Workflow", (), {"id": uuid4(), "is_active": True})()

    monkeypatch.setattr(
        "src.worker.routers.pubsub.get_session",
        fake_session,
    )
    monkeypatch.setattr(
        "src.worker.services.workflow_resolver.WorkflowResolver.resolve",
        fake_resolve,
    )
    monkeypatch.setattr(
        "src.worker.services.executor.Executor.execute",
        fake_execute,
    )
    payload = make_push_payload(envelope)
    response = await client.post("/worker/pubsub/push", json=payload)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_worker_retry_on_db_error(client, monkeypatch, envelope, async_session):
    async def broken_create_pending(*_, **__):
        raise OperationalError("INSERT execution logs", {}, None)

    monkeypatch.setattr(
        "src.repositories.execution_log.ExecutionLogRepository.create_pending",
        broken_create_pending,
    )

    payload = make_push_payload(envelope)
    response = await client.post("/worker/pubsub/push", json=payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    repo = ExecutionLogRepository(async_session)
    logs = await repo.list(event_id=envelope["event_id"])
    assert len(logs) == 0, "DB error shouldn't create execution logs"


@pytest.mark.asyncio
async def test_worker_fatal_on_validation_error(client, monkeypatch, envelope):
    from pydantic import BaseModel

    class Dummy(BaseModel):
        value: int

    def bad_decode(_):
        Dummy(value="not-int")

    monkeypatch.setattr(
        "src.worker.routers.pubsub.decode_pubsub_message",
        bad_decode,
    )
    payload = make_push_payload(envelope)
    response = await client.post("/worker/pubsub/push", json=payload)
    assert response.status_code == status.HTTP_200_OK
