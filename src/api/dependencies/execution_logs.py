from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.repositories.execution_log import ExecutionLogRepository


def get_execution_log_repo(
    session: AsyncSession = Depends(get_session),
) -> ExecutionLogRepository:
    return ExecutionLogRepository(session)
