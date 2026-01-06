from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowTriggerPayload(BaseModel):
    workflow_id: UUID = Field(..., description="Workflow identifier")
    source: str | None = None
