from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.job_repository import PostgresJobRepository
from app.pipeline import FILM_PIPELINE


class PipelineGraphService:
    """Persists the actual job-to-job dependency graph for a film run."""

    async def create_graph(
        self,
        session: AsyncSession,
        film_id: UUID,
        environment_id: UUID,
        payload: dict | None = None,
    ) -> list[UUID]:
        repository = PostgresJobRepository(session)
        jobs_by_stage = {}
        payload = payload or {}

        for stage in FILM_PIPELINE:
            job = await repository.create(
                film_id=film_id,
                environment_id=environment_id,
                job_type=stage.name,
                payload={"film": payload},
            )
            jobs_by_stage[stage.name] = job

        for stage in FILM_PIPELINE:
            job = jobs_by_stage[stage.name]
            for dependency in stage.depends_on:
                await session.execute(
                    __import__("sqlalchemy").text(
                        "INSERT INTO job_dependencies (job_id, depends_on_job_id) VALUES (:job_id, :dependency_id)"
                    ),
                    {"job_id": str(job.job_id), "dependency_id": str(jobs_by_stage[dependency].job_id)},
                )

        await session.flush()
        return [job.job_id for job in jobs_by_stage.values()]
