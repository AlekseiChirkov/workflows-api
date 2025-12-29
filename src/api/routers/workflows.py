from uuid import UUID

from fastapi import APIRouter, Depends
from src.api.dependencies.workflows import get_workflow_service
from src.api.dependencies.auth import authorize
from src.models.workflow import WorkflowCreate, WorkflowRead, WorkflowUpdate
from src.services.workflow import WorkflowService

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    dependencies=[Depends(authorize)],
)


@router.get(
    "/{workflow_id}",
    response_model=WorkflowRead,
    summary="Get workflow by id",
    description="Get workflow by id",
    responses={
        401: {"description": "Unauthorized - invalid or missing API key"},
    },
)
async def get_workflow(
    workflow_id: UUID,
    service: WorkflowService = Depends(get_workflow_service),
):
    return await service.get_workflow(workflow_id)


@router.get(
    "",
    response_model=list[WorkflowRead],
    summary="List workflows",
    description="List workflows",
    responses={
        401: {"description": "Unauthorized - invalid or missing API key"},
    },
)
async def list_workflows(
    service: WorkflowService = Depends(get_workflow_service),
):
    return await service.list_workflows()


@router.post(
    "",
    response_model=WorkflowRead,
    summary="Create workflow",
    description="Create workflow",
    responses={
        400: {
            "description": "Workflow already exists",
            "content": {
                "application/json": {
                    "example": {
                        "error": "WorkflowAlreadyExists",
                        "message": "Workflow 'Onboarding' already exists.",
                    }
                }
            },
        },
        401: {"description": "Unauthorized - invalid or missing API key"},
    },
)
async def create_workflow(
    payload: WorkflowCreate,
    service: WorkflowService = Depends(get_workflow_service),
):
    return await service.create_workflow(payload.model_dump())


@router.put(
    "/{workflow_id}",
    response_model=WorkflowRead,
    summary="Update workflow by id",
    description="Update workflow by id",
    responses={
        401: {"description": "Unauthorized - invalid or missing API key"},
    },
)
async def update_workflow(
    workflow_id: UUID,
    payload: WorkflowUpdate,
    service: WorkflowService = Depends(get_workflow_service),
):
    return await service.update_workflow(workflow_id, payload.model_dump(exclude_unset=True))


@router.delete(
    "/{workflow_id}",
    summary="Delete workflow by id",
    description="Delete workflow by id",
    responses={
        401: {"description": "Unauthorized - invalid or missing API key"},
    },
)
async def delete_workflow(
    workflow_id: UUID,
    service: WorkflowService = Depends(get_workflow_service),
):
    await service.delete_workflow(workflow_id)
    return {"status": "deleted"}
