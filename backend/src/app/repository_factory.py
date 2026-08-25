from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.postgres_repository import PostgresRepository
from app.repository import InMemoryRepository

_memory_repository = InMemoryRepository()


async def get_repository(
    session: AsyncSession = Depends(get_db),
):
    if settings.database_url:
        return PostgresRepository(session)
    return _memory_repository
