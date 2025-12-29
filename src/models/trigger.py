from pydantic import BaseModel, Field
from uuid import UUID


class BaseTrigger(BaseModel):
    type: str = Field(..., description="Trigger type (http, cron, pub/sub)")
    config: dict = Field(default_factory=dict, description="Trigger configuration")


class TriggerCreate(BaseTrigger):
    pass


class TriggerRead(BaseTrigger):
    id: UUID
    workflow_id: UUID
