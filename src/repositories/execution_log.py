from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
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

    async def create_pending(self, payload: dict) -> tuple[ExecutionLog, bool]:
        stmt = (
            insert(ExecutionLog)
            .values(**payload)
            .on_conflict_do_nothing(
                index_elements=["event_id", "workflow_id"]
            )
            .returning(ExecutionLog)
        )
        result = await self.session.execute(stmt)
        log = result.scalar_one_or_none()
        if log:
            return log, True

        existing = await self.get_by_event(payload["event_id"], payload["workflow_id"])
        return existing, False

    async def increment_attempts(self, log: ExecutionLog, error: str | None = None) -> ExecutionLog:
        log.attempts += 1
        if error:
            log.last_error = error

        await self.session.flush()
        return log

    async def get_by_event(self, event_id, workflow_id) -> ExecutionLog | None:
        stmt = select(ExecutionLog).where(
            ExecutionLog.event_id == event_id,
            ExecutionLog.workflow_id == workflow_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_finished(self, log: ExecutionLog, result: dict) -> ExecutionLog:
        for field, value in result.items():
            setattr(log, field, value)

        await self.session.flush()
        return log

    async def list(
        self,
        *,
        workflow_id=None,
        event_id=None,
        status=None,
        trace_id=None,
        queued_to_dlq: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ExecutionLog]:
        stmt = (
            select(ExecutionLog)
            .order_by(ExecutionLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if workflow_id:
            stmt = stmt.where(ExecutionLog.workflow_id == workflow_id)
        if event_id:
            stmt = stmt.where(ExecutionLog.event_id == event_id)
        if status:
            stmt = stmt.where(ExecutionLog.status == status)
        if trace_id:
            stmt = stmt.where(ExecutionLog.trace_id == trace_id)
        if queued_to_dlq is not None:
            stmt = stmt.where(ExecutionLog.queued_to_dlq == queued_to_dlq)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
