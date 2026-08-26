from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JobModel


class PostgresJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        film_id: UUID,
        environment_id: UUID,
        job_type: str,
        payload: dict,
        max_attempts: int = 3,
        idempotency_key: str | None = None,
    ) -> JobModel:
        if idempotency_key:
            existing = await self.session.scalar(
                select(JobModel).where(
                    JobModel.film_id == film_id,
                    JobModel.idempotency_key == idempotency_key,
                )
            )
            if existing is not None:
                return existing
        job = JobModel(
            job_id=uuid4(),
            film_id=film_id,
            environment_id=environment_id,
            job_type=job_type,
            payload=payload,
            max_attempts=max_attempts,
            idempotency_key=idempotency_key,
            status="queued",
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def get(self, job_id: UUID) -> JobModel | None:
        return await self.session.get(JobModel, job_id)

    async def list_for_film(self, film_id: UUID) -> list[JobModel]:
        result = await self.session.execute(select(JobModel).where(JobModel.film_id == film_id).order_by(JobModel.created_at))
        return list(result.scalars().all())

    async def recover_stale_running(self, lease_seconds: int = 900) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=lease_seconds)
        result = await self.session.execute(
            text("""
                UPDATE jobs
                SET status = CASE WHEN attempts < max_attempts THEN 'retrying' ELSE 'failed' END,
                    worker_id = NULL,
                    lease_until = NULL,
                    error_code = 'worker_lease_expired',
                    retry_count = retry_count + 1,
                    updated_at = now()
                WHERE status = 'running'
                  AND (lease_until IS NOT NULL AND lease_until < :now OR
                       lease_until IS NULL AND started_at < :cutoff)
                RETURNING job_id
            """),
            {"cutoff": cutoff, "now": datetime.now(timezone.utc)},
        )
        count = len(result.fetchall())
        await self.session.flush()
        return count

    async def claim_next_ready(self) -> JobModel | None:
        result = await self.session.execute(
            text("""
                SELECT j.job_id
                FROM jobs j
                WHERE j.status IN ('queued', 'retrying')
                  AND j.scheduled_at <= now()
                  AND j.attempts < j.max_attempts
                  AND NOT EXISTS (
                    SELECT 1 FROM job_dependencies d
                    JOIN jobs dep ON dep.job_id = d.depends_on_job_id
                    WHERE d.job_id = j.job_id AND dep.status <> 'completed'
                  )
                ORDER BY j.scheduled_at, j.created_at
                FOR UPDATE OF j SKIP LOCKED LIMIT 1
            """)
        )
        row = result.first()
        if row is None:
            return None
        job = await self.session.get(JobModel, row[0])
        if job is None:
            return None
        now = datetime.now(timezone.utc)
        job.status = "running"
        job.attempts += 1
        job.started_at = now
        job.lease_until = now + timedelta(seconds=900)
        job.updated_at = now
        await self.session.flush()
        return job

    async def complete(self, job: JobModel, result: dict) -> JobModel:
        now = datetime.now(timezone.utc)
        job.status = "completed"
        job.result = result
        job.completed_at = now
        job.lease_until = None
        job.worker_id = None
        job.updated_at = now
        job.error_code = None
        await self.session.flush()
        return job

    async def fail(self, job: JobModel, error_code: str, retry: bool = True) -> JobModel:
        now = datetime.now(timezone.utc)
        job.status = "retrying" if retry and job.attempts < job.max_attempts else "failed"
        job.error_code = error_code
        job.worker_id = None
        job.lease_until = None
        job.retry_count += 1
        job.updated_at = now
        await self.session.flush()
        return job

    async def cancel(self, job: JobModel) -> JobModel:
        if job.status in {"queued", "retrying"}:
            job.status = "cancelled"
            job.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
        return job
