from typing import Any

from pydantic import BaseModel

from src.db.models import Workflow
from src.events.schema import EventEnvelope


class ActionResult(BaseModel):
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
    retryable: bool = False
    duration: float | None = None


class ExecutionContext(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    event: EventEnvelope
    workflow: Workflow
    trace_id: str