from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence
from sqlalchemy.exc import IntegrityError

from src.db.models import Workflow
from src.core.exceptions import WorkflowNotFound, WorkflowAlreadyExists


class WorkflowRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, workflow_id) -> Workflow:
        result = await self.session.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise WorkflowNotFound(f"Workflow with id {workflow_id} not found")

        return workflow

    async def get_all(self) -> Sequence[Workflow]:
        result = await self.session.execute(select(Workflow))
        return result.scalars().all()

    async def create(self, data: dict) -> Workflow:
        workflow = Workflow(**data)
        self.session.add(workflow)

        try:
            await self.session.flush()
        except IntegrityError:
            raise WorkflowAlreadyExists(f"Workflow with name {data.get('name')} already exists")
        return workflow

    async def update(self, workflow: Workflow, data: dict) -> Workflow:
        for field, value in data.items():
            setattr(workflow, field, value)

        await self.session.flush()
        return workflow

    async def delete(self, workflow: Workflow) -> None:
        await self.session.delete(workflow)
        await self.session.flush()
