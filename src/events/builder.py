from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from src.events.schema import EventEnvelope


def build_event_envelope(
        *,
        event_type: str,
        payload: dict[str, Any],
        trace_id: str,
        source: str ="api",
        version: int = 1,
) -> EventEnvelope:
    return EventEnvelope(
        event_id=uuid4(),
        event_type=event_type,
        version=version,
        timestamp=datetime.now(timezone.utc),
        source=source,
        trace_id=trace_id,
        payload=payload,
    )