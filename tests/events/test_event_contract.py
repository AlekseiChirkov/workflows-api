from src.events.builder import build_event_envelope


def test_event_envelope_contract():
    envelope = build_event_envelope(
        event_type="workflow.triggered",
        payload={"workflow_id": "123"},
        trace_id="trace-abc",
    )

    data = envelope.model_dump()

    assert "event_id" in data
    assert data["event_type"] == "workflow.triggered"
    assert data["version"] == 1
    assert "timestamp" in data
    assert "trace_id" in data
    assert data["payload"]["workflow_id"] == "123"