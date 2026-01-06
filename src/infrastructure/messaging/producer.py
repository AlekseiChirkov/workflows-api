import json
import logging
from typing import Optional

from google.cloud import pubsub_v1
from google.api_core.exceptions import GoogleAPIError

from src.events.schema import EventEnvelope

logger = logging.getLogger(__name__)


class PubSubProducer:
    def __init__(self, project_id: str, topic_name: str) -> None:
        self._topic_path = f"projects/{project_id}/topics/{topic_name}"

        self._publisher = pubsub_v1.PublisherClient(
            batch_settings=pubsub_v1.types.BatchSettings(
                max_bytes=1024 * 1024,
                max_latency=0.1,
                max_messages=100,
            )
        )

    def publish(self, event: EventEnvelope) -> str:
        data = json.dumps(event.model_dump(mode="json")).encode("utf-8")

        logging_payload = {
            "event_id": event.event_id,
            "event_type": event.event_type,
        }

        try:
            future = self._publisher.publish(self._topic_path, data=data)
            message_id = future.result(timeout=5)

            logger.info(
                "Event published",
                extra=logging_payload
            )

            return message_id
        except GoogleAPIError:
            logger.exception(
                "Failed to publish event",
                extra=logging_payload
            )
            raise

    def close(self) -> None:
        self._publisher.transport.close()