import base64
import json
from datetime import datetime, timezone

import pytest
from fastapi import status


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
