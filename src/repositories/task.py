from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence

from src.db.models import Task
from src.core.exceptions import WorkflowNotFound


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workflow_id: UUID, payload: dict) -> Task:
        task = Task(
            workflow_id=workflow_id,
            payload=payload,
            status="pending",
        )

        self.session.add(task)
        await self.session.flush()
        return task

    async def list_by_workflow(self, workflow_id: UUID) -> Sequence[Task]:
        result = await self.session.execute(
            select(Task).where(Task.workflow_id == workflow_id)
        )
        return result.scalars().all()

    async def update_status(self, task: Task, status: str) -> Task:
        task.status = status
        await self.session.flush()
        return task
