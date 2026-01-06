from src.events.builder import build_event_envelope
from src.events.types import WORKFLOW_TRIGGERED


def test_build_event_envelope():
    envelope = build_event_envelope(
        event_type=WORKFLOW_TRIGGERED,
        payload={"workflow_id": "123"},
        trace_id="test-trace-id",
    )

    assert envelope.event_type == "workflow.triggered"
    assert envelope.version == 1
    assert envelope.trace_id == "test-trace-id"