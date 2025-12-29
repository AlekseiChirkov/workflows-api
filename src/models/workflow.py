from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from src.models.task import TaskRead
from src.models.trigger import TriggerRead


class BaseWorkflow(BaseModel):
    name: str
    description: str
    is_active: bool
    status: str
    created_at: datetime
    updated_at: datetime


class WorkflowCreate(BaseWorkflow):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Customer Onboarding"
            }
        }
    )


class WorkflowUpdate(BaseModel):
    name: str | None = None
    status: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Customer Onboarding",
                "status": "draft"
            }
        }
    )


class WorkflowRead(BaseWorkflow):
    id: UUID
    tasks: List[TaskRead] = []
    triggers: List[TriggerRead] = []

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "New Customer Onboarding",
                "status": "draft",
                "tasks": [],
                "triggers": []
            }
        }
    )


class WorkflowInternal(WorkflowRead):
    pass