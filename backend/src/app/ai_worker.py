from __future__ import annotations

import asyncio
import logging
import os

from app.ai_engine_client import AIEngineClient
from app.db import session_factory
from app.job_repository import PostgresJobRepository
from app.models import FilmModel

logger = logging.getLogger(__name__)


class AIJobWorker:
    """Persistent PostgreSQL queue worker for the dedicated AI engine."""

    def __init__(self, poll_seconds: float | None = None) -> None:
        self.poll_seconds = poll_seconds or float(os.getenv("AI_WORKER_POLL_SECONDS", "1"))
        self.client = AIEngineClient()
        self._stop = asyncio.Event()

    def stop(self) -> None:
        self._stop.set()

    async def run(self) -> None:
        if session_factory is None:
            raise RuntimeError("DATABASE_URL is required for AI worker execution")
        while not self._stop.is_set():
            try:
                processed = await self.process_one()
                if not processed:
                    await asyncio.sleep(self.poll_seconds)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("AI worker iteration failed")
                await asyncio.sleep(self.poll_seconds)

    async def process_one(self) -> bool:
        if session_factory is None:
            raise RuntimeError("DATABASE_URL is required for AI worker execution")
        async with session_factory() as session:
            repository = PostgresJobRepository(session)
            job = await repository.claim_next_ready()
            if job is None:
                await session.rollback()
                return False
            film = await session.get(FilmModel, job.film_id)
            if film is None:
                await repository.fail(job, "film_not_found", retry=False)
                await session.commit()
                return True
            await session.commit()
            job_id, client_id, film_id, environment_id = job.job_id, film.client_id, job.film_id, job.environment_id
            operation, payload = job.job_type, job.payload

        try:
            result = await self.client.execute_job(job_id=job_id, client_id=client_id, film_id=film_id, operation=operation, payload=payload, environment_id=environment_id)
        except Exception as exc:
            async with session_factory() as session:
                repository = PostgresJobRepository(session)
                persisted = await repository.get(job_id)
                if persisted is not None:
                    await repository.fail(persisted, type(exc).__name__, retry=True)
                    await session.commit()
            return True

        async with session_factory() as session:
            repository = PostgresJobRepository(session)
            persisted = await repository.get(job_id)
            if persisted is not None:
                await repository.complete(persisted, result)
                await session.commit()
        return True
