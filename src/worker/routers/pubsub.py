from fastapi import APIRouter, Request, Response, status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def healthcheck():
    return {"status": "ok"}


@router.post("/pubsub/push")
async def pubsub_push(request: Request):
    return Response(status_code=status.HTTP_200_OK)