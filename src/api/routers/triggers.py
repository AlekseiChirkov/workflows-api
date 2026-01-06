from uuid import UUID

from fastapi import APIRouter, Request, HTTPException, status, Depends

from src.api.dependencies import get_event_producer, authorize
from src.api.schemas import WorkflowTriggerPayload
from src.core.request_context import get_request_id
from src.events.builder import build_event_envelope

router = APIRouter(
    prefix="/triggers",
    tags=["triggers"],
)


@router.post(
    "/webhook/{workflow_id}",
    status_code=status.HTTP_202_ACCEPTED
)
async def trigger_workflow(
        workflow_id: UUID,
        payload: WorkflowTriggerPayload,
        request: Request,
):
    trace_id = get_request_id()
    envelope = build_event_envelope(
        event_type="workflow.triggered",
        payload={
            "workflow_id": workflow_id,
            "source": payload.source,
        },
        trace_id=trace_id,
    )

    producer = get_event_producer(request)


    try:
        producer.publish(envelope)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Event pipeline unavailable: {str(e)}",
        )

    return {
        "status": "accepted",
        "event_id": envelope.event_id,
        "trace_id": trace_id,
    }