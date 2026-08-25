from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JobModel


class JobScheduler:
    """Atomically claims dependency-ready jobs for workers."""

    async def claim_next(self, session: AsyncSession, environment_id: UUID) -> JobModel | None:
        query = text("""
            SELECT j.job_id
            FROM jobs j
            WHERE j.environment_id = :environment_id
              AND j.status IN ('queued', 'retrying')
              AND j.scheduled_at <= now()
              AND NOT EXISTS (
                  SELECT 1
                  FROM job_dependencies d
                  JOIN jobs parent ON parent.job_id = d.depends_on_job_id
                  WHERE d.job_id = j.job_id
                    AND parent.status <> 'succeeded'
              )
            ORDER BY j.scheduled_at, j.created_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        """)
        result = await session.execute(query, {"environment_id": str(environment_id)})
        row = result.first()
        if row is None:
            return None

        job = await session.get(JobModel, row.job_id, with_for_update=True)
        if job is None:
            return None
        job.status = "running"
        job.attempts += 1
        job.started_at = datetime.now(timezone.utc)
        job.updated_at = datetime.now(timezone.utc)
        await session.flush()
        return job

    async def succeed(self, session: AsyncSession, job: JobModel, result: dict | None = None) -> None:
        job.status = "succeeded"
        job.result = result or {}
        job.completed_at = datetime.now(timezone.utc)
        job.updated_at = datetime.now(timezone.utc)
        await session.flush()

    async def fail(self, session: AsyncSession, job: JobModel, error_code: str) -> None:
        job.error_code = error_code
        job.updated_at = datetime.now(timezone.utc)
        if job.attempts < job.max_attempts:
            job.status = "retrying"
        else:
            job.status = "failed"
            job.completed_at = datetime.now(timezone.utc)
        await session.flush()
