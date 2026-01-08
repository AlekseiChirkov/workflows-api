from uuid import uuid4

import pytest_asyncio

from src.db.models import Workflow


@pytest_asyncio.fixture
async def active_workflow(async_session):
    workflow = Workflow(
        id=uuid4(),
        is_active=True,
    )
    async_session.add(workflow)
    await async_session.commit()
    return workflow


@pytest_asyncio.fixture
async def inactive_workflow(async_session):
    workflow = Workflow(
        id=uuid4(),
        is_active=False,
    )
    async_session.add(workflow)
    await async_session.commit()
    return workflow
