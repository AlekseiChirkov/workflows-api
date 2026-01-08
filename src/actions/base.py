from abc import ABC, abstractmethod

from src.models.actions import ExecutionContext, ActionResult


class BaseAction(ABC):
    @abstractmethod
    async def run(self, context: ExecutionContext) -> ActionResult:...
