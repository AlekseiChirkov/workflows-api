from sqlalchemy.ext.asyncio import AsyncSession

from src.events.schema import EventEnvelope
from src.db.models import Workflow
from src.repositories.workflow import WorkflowRepository
from src.core.exceptions import (
    WorkflowNotFound,
    WorkflowInactive,
)


class WorkflowResolver:
    def __init__(self, session: AsyncSession):
        self._repo = WorkflowRepository(session)

    async def resolve(self, event: EventEnvelope) -> Workflow:
        workflow_id = event.payload.get("workflow_id")
        if not workflow_id:
            raise WorkflowNotFound("workflow_id missing in event payload")

        workflow = await self._repo.get_by_id(workflow_id)

        if not workflow:
            raise WorkflowNotFound(f"Workflow {workflow_id} not found")

        if not workflow.is_active:
            raise WorkflowInactive(f"Workflow {workflow_id} is inactive")

        return workflow