import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.db.session import get_session
from src.events.schema import EventEnvelope
from src.worker.main import create_app

pytest_plugins = [
    "tests.fixtures.workflow",
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def async_session():
    async for session in get_session():
        yield session


@pytest.fixture
def envelope():
    return EventEnvelope(
        event_id=uuid4(),
        event_type="workflow.triggered",
        version=1,
        timestamp=datetime.now(timezone.utc),
        source="api",
        payload={"workflow_id": uuid4()},
        trace_id="test",
    ).model_dump(mode="json")
