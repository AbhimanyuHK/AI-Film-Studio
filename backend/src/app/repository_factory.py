from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_optional_db
from app.postgres_repository import PostgresRepository
from app.repository import InMemoryRepository

_memory_repository = InMemoryRepository()


async def get_repository(
    session: AsyncSession | None = Depends(get_optional_db),
):
    """Select Postgres when configured, otherwise use the async in-memory repository."""
    if settings.database_url:
        if session is None:
            raise RuntimeError("Database configuration is present but no database session is available")
        return PostgresRepository(session)
    return _memory_repository
