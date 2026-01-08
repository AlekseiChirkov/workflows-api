import base64
import json
import logging

from src.worker.models.pubsub_push import PubSubPushBody
from src.events.schema import EventEnvelope

logger = logging.getLogger(__name__)


def decode_pubsub_message(push_body: PubSubPushBody) -> EventEnvelope:
    if not push_body.message.data:
        raise ValueError("Empty Pub/Sub message data")

    try:
        raw_bytes = base64.b64decode(push_body.message.data)
        payload = json.loads(raw_bytes.decode("utf-8"))
    except Exception as e:
        logger.warning("Failed to decode Pub/Sub payload", exc_info=e)
        raise ValueError("Malformed Pub/Sub payload")

    try:
        return EventEnvelope.model_validate(payload)
    except Exception as e:
        logger.warning("Invalid Envelope", exc_info=e)
        raise ValueError("Invalid Envelope")
