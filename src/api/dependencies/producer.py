from fastapi import Request

from src.infrastructure.messaging.producer import PubSubProducer


def get_event_producer(request: Request) -> PubSubProducer:
    return request.app.state.event_producer
