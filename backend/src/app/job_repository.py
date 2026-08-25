from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
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

    async def cancel(self, job: JobModel) -> JobModel:
        if job.status in {"queued", "retrying"}:
            job.status = "cancelled"
            job.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
        return job
