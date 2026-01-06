from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from src.models.task import TaskRead
from src.models.trigger import TriggerRead


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Customer Onboarding",
                "description": "Onboarding flow",
                "is_active": True
            }
        }
    )



class WorkflowUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    status: str | None = None


class WorkflowRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    is_active: bool
    status: str
    created_at: datetime
    updated_at: datetime | None

    tasks: list[TaskRead] = []
    triggers: list[TriggerRead] = []

    model_config = ConfigDict(from_attributes=True)
