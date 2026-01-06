from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime, timezone

import pytest
from google.api_core.exceptions import GoogleAPIError

from src.infrastructure.messaging.producer import PubSubProducer
from src.events.schema import EventEnvelope


def test_pubsub_producer_publish_success(mocker):
    mock_publisher = MagicMock()
    mock_future = MagicMock()
    mock_future.result.return_value = "message-id-123"
    mock_publisher.publish.return_value = mock_future

    mocker.patch(
        "src.infrastructure.messaging.producer.pubsub_v1.PublisherClient",
        return_value=mock_publisher,
    )

    producer = PubSubProducer(
        project_id="test-project",
        topic_name="workflow-events",
    )

    event = EventEnvelope(
        event_id=uuid4(),
        event_type="workflow.triggered",
        version=1,
        timestamp=datetime.now(timezone.utc),
        source="api",
        trace_id="trace-123",
        payload={"workflow_id": str(uuid4())},
    )

    message_id = producer.publish(event)

    assert message_id == "message-id-123"
    mock_publisher.publish.assert_called_once()


def test_pubsub_producer_publish_error(mocker):
    mock_publisher = MagicMock()
    mock_future = MagicMock()
    mock_future.result.side_effect = GoogleAPIError("boom")
    mock_publisher.publish.return_value = mock_future

    mocker.patch(
        "src.infrastructure.messaging.producer.pubsub_v1.PublisherClient",
        return_value=mock_publisher,
    )

    producer = PubSubProducer(
        project_id="test-project",
        topic_name="workflow-events",
    )

    event = EventEnvelope(
        event_id=uuid4(),
        event_type="workflow.triggered",
        version=1,
        timestamp=datetime.now(timezone.utc),
        source="api",
        trace_id="trace-123",
        payload={"workflow_id": "123"},
    )

    with pytest.raises(GoogleAPIError):
        producer.publish(event)
