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


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
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
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from src.core.config import settings
    
    DATABASE_URL = (
        "postgresql+asyncpg://"
        f"{settings.DB_USER}:{settings.DB_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    
    engine = create_async_engine(DATABASE_URL, echo=False, poolclass=None)
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_factory() as session:
        yield session
        await session.rollback()
    
    await engine.dispose()


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
