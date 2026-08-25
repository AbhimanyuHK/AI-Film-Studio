from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.job_scheduler import JobScheduler
from app.worker import JobWorker


class ProductionWorker:
    """Coordinates database job claiming with provider-specific handlers."""

    def __init__(self, worker: JobWorker | None = None) -> None:
        self.worker = worker or JobWorker()
        self.scheduler = JobScheduler()

    def register(self, job_type: str, handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]) -> None:
        self.worker.register(job_type, handler)

    async def run_once(self, session: AsyncSession, environment_id: UUID) -> bool:
        job = await self.scheduler.claim_next(session, environment_id)
        if job is None:
            return False
        try:
            result = await self.worker.execute(job.job_type, job.payload)
            await self.scheduler.succeed(session, job, result)
        except Exception:
            await self.scheduler.fail(session, job, "WORKER_EXECUTION_FAILED")
        await session.commit()
        return True
