from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.repositories.task import TaskRepository


def get_task_repo(session: AsyncSession = Depends(get_session)) -> TaskRepository:
    return TaskRepository(session)