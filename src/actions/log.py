from src.actions.base import BaseAction, ExecutionContext, ActionResult


class LogAction(BaseAction):
    async def run(self, context: ExecutionContext) -> ActionResult:
        payload = {
            "workflow_id": str(context.workflow.id),
            "event_id": str(context.event.event_id),
            "trace_id": context.trace_id,
        }
        return ActionResult(status="success", result=payload)
