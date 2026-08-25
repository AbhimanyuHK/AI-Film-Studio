from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JobModel


class PostgresJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, film_id: UUID, environment_id: UUID, job_type: str, payload: dict, max_attempts: int = 3) -> JobModel:
        job = JobModel(job_id=uuid4(), film_id=film_id, environment_id=environment_id, job_type=job_type, payload=payload, max_attempts=max_attempts, status="queued")
        self.session.add(job)
        await self.session.flush()
        return job

    async def get(self, job_id: UUID) -> JobModel | None:
        return await self.session.get(JobModel, job_id)

    async def list_for_film(self, film_id: UUID) -> list[JobModel]:
        result = await self.session.execute(select(JobModel).where(JobModel.film_id == film_id).order_by(JobModel.created_at))
        return list(result.scalars().all())

    async def claim_next_ready(self) -> JobModel | None:
        """Atomically claim one runnable job; PostgreSQL SKIP LOCKED makes this safe for many workers."""
        result = await self.session.execute(
            text("""
                SELECT j.job_id
                FROM jobs j
                WHERE j.status IN ('queued', 'retrying')
                  AND j.scheduled_at <= now()
                  AND j.attempts < j.max_attempts
                  AND NOT EXISTS (
                    SELECT 1
                    FROM job_dependencies d
                    JOIN jobs dep ON dep.job_id = d.depends_on_job_id
                    WHERE d.job_id = j.job_id
                      AND dep.status <> 'completed'
                  )
                ORDER BY j.created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            """)
        )
        row = result.first()
        if row is None:
            return None
        job = await self.session.get(JobModel, row[0])
        if job is None:
            return None
        job.status = "running"
        job.attempts += 1
        job.started_at = datetime.now(timezone.utc)
        job.updated_at = job.started_at
        await self.session.flush()
        return job

    async def complete(self, job: JobModel, result: dict) -> JobModel:
        now = datetime.now(timezone.utc)
        job.status = "completed"
        job.result = result
        job.completed_at = now
        job.updated_at = now
        job.error_code = None
        await self.session.flush()
        return job

    async def fail(self, job: JobModel, error_code: str, retry: bool = True) -> JobModel:
        now = datetime.now(timezone.utc)
        job.status = "retrying" if retry and job.attempts < job.max_attempts else "failed"
        job.error_code = error_code
        job.updated_at = now
        await self.session.flush()
        return job

    async def cancel(self, job: JobModel) -> JobModel:
        if job.status in {"queued", "retrying"}:
            job.status = "cancelled"
            job.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
        return job
