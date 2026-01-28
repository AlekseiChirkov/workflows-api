from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExecutionLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    event_id: UUID
    trace_id: str
    action: str
    status: str
    result: dict[str, Any] | None = None
    payload_snapshot: dict[str, Any] | None = None
    error: str | None = None
    last_error: str | None = None
    retryable: bool
    attempts: int
    queued_to_dlq: bool
    duration: float | None = None
    action_duration_ms: float | None = None
    created_at: datetime


class ExecutionLogListResponse(BaseModel):
    items: list[ExecutionLogItem]
    count: int
