from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ExecutionLog


class ExecutionLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payload: dict) -> ExecutionLog:
        log = ExecutionLog(**payload)
        self.session.add(log)
        await self.session.flush()
        return log