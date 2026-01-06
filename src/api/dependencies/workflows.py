from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.tasks import get_task_repo
from src.repositories.task import TaskRepository
from src.repositories.workflow import WorkflowRepository
from src.db.session import get_session
from src.services.workflow import WorkflowService


def get_workflow_repo(session: AsyncSession = Depends(get_session)) -> WorkflowRepository:
    return WorkflowRepository(session)


def get_workflow_service(
        repo: WorkflowRepository = Depends(get_workflow_repo),
        task: TaskRepository = Depends(get_task_repo),
        session: AsyncSession = Depends(get_session),
) -> WorkflowService:
    return WorkflowService(repo, task, session)

