from typing import List, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import WorkflowNotFound
from src.db.models import Workflow, Task
from src.repositories.task import TaskRepository
from src.repositories.workflow import WorkflowRepository


class WorkflowService:
    def __init__(self, workflow_repo: WorkflowRepository, task_repo: TaskRepository, session: AsyncSession):
        self.workflow_repo = workflow_repo
        self.task_repo = task_repo
        self.session = session

    async def get_workflow(self, workflow_id: UUID) -> Workflow:
        return await self.workflow_repo.get_by_id(workflow_id)

    async def list_workflows(self) -> List[Workflow]:
        return await self.workflow_repo.get_all()

    async def update_workflow(self, workflow_id: UUID, payload: Dict) -> Workflow:
        async with self.session.begin():
            workflow = await self.workflow_repo.get_by_id(workflow_id)
            updated_workflow = await self.workflow_repo.update(workflow, payload)
        return updated_workflow

    async def delete_workflow(self, workflow_id: UUID) -> None:
        workflow = await self.workflow_repo.get_by_id(workflow_id)
        await self.workflow_repo.delete(workflow)

    async def create_workflow(self, payload: Dict) -> Workflow:
        async with self.session.begin():
            workflow = await self.workflow_repo.create(payload)
        return workflow

    async def create_task(self, workflow_id: UUID, payload: Dict) -> Task:
        async with self.session.begin():
            workflow = await self.workflow_repo.get_by_id(workflow_id)
            if not workflow.is_active:
                raise WorkflowNotFound(f"Workflow is not active")

            task = await self.task_repo.create(workflow_id, payload)
            workflow.is_active = True
            task.status = "running"

            await self.session.flush()
            return task
