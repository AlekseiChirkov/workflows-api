from pydantic import BaseModel

from typing import Optional, Dict


class PubSubMessage(BaseModel):
    messageId: str
    data: Optional[str] = None
    attributes: Dict[str, str] = {}
    publishTime: str


class PubSubPushBody(BaseModel):
    message: PubSubMessage
    subscription: str
