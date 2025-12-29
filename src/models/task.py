from pydantic import BaseModel, Field
from uuid import UUID


class BaseTask(BaseModel):
    name: str = Field(..., description="Name of the task")
    type: str = Field(..., description="Type of the task (http_call, email, delay)")
    config: dict = Field(default_factory=dict, description="Task configuration")


class TaskCreate(BaseTask):
    pass


class TaskRead(BaseTask):
    id: UUID
    workflow_id: UUID
