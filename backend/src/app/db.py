from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


if settings.database_url:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
else:
    engine = None
    session_factory = None


async def get_db() -> AsyncIterator[AsyncSession]:
    if session_factory is None:
        raise RuntimeError("DATABASE_URL is required for database-backed execution")
    async with session_factory() as session:
        yield session


async def get_optional_db() -> AsyncIterator[AsyncSession | None]:
    """Yield a database session when configured, otherwise None for local tests."""
    if session_factory is None:
        yield None
        return
    async with session_factory() as session:
        yield session
