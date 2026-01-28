from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies.auth import authorize
from src.api.dependencies.execution_logs import get_execution_log_repo
from src.models.execution_log import ExecutionLogListResponse
from src.repositories.execution_log import ExecutionLogRepository


router = APIRouter(
    prefix="/execution-logs",
    tags=["execution-logs"],
    dependencies=[Depends(authorize)],
)


@router.get(
    "",
    response_model=ExecutionLogListResponse,
    summary="List execution logs with filters",
)
async def list_execution_logs(
    workflow_id: UUID | None = None,
    event_id: UUID | None = None,
    status: str | None = None,
    trace_id: str | None = None,
    queued_to_dlq: bool | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo: ExecutionLogRepository = Depends(get_execution_log_repo),
) -> ExecutionLogListResponse:
    logs = await repo.list(
        workflow_id=workflow_id,
        event_id=event_id,
        status=status,
        trace_id=trace_id,
        queued_to_dlq=queued_to_dlq,
        limit=limit,
        offset=offset,
    )
    return ExecutionLogListResponse(items=logs, count=len(logs))
