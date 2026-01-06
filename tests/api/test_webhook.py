from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4

from src.main import create_app


def test_webhook_triggers_publish():
    app = create_app()

    mock_producer = MagicMock()
    app.state.event_producer = mock_producer

    client = TestClient(app)

    workflow_id = str(uuid4())

    response = client.post(
        f"/triggers/webhook/{workflow_id}",
        json={"workflow_id": workflow_id},
    )

    assert response.status_code == 202
    mock_producer.publish.assert_called_once()
