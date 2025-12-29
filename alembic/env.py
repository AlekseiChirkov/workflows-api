import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from dotenv import load_dotenv
load_dotenv()

from src.core.config import settings
from src.db.base import Base
from src.db.models import *  # noqa


config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL)

    async def run_async_migrations():
        async with connectable.connect() as async_connection:
            await async_connection.run_sync(do_run_migrations)

    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        context.run_migrations()

    asyncio.run(run_async_migrations())


run_migrations_online()
