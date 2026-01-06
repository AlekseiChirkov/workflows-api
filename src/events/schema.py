from uuid import UUID

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any


class EventEnvelope(BaseModel):
    event_id: UUID = Field(..., description="Unique event identifier (UUID)")
    event_type: str = Field(..., description="Event type, e.g. workflow.triggered")
    version: int = Field(..., description="Event schema version")
    timestamp: datetime = Field(..., description="UTC event creation time")
    source: str = Field(..., description="Producer service name")
    trace_id: str = Field(..., description="Request / correlation id")
    payload: dict[str, Any]

    model_config = {
        "extra": "ignore",
        "json_schema_extra": {
            "example": {
                "event_id": "uuid",
                "event_type": "workflow.triggered",
                "version": 1,
                "timestamp": "2025-01-01T12:00:00Z",
                "source": "api",
                "trace_id": "req-123",
                "payload": {
                    "workflow_id": "uuid"
                }
            }
        }
    }