from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.job_repository import PostgresJobRepository
from app.pipeline import FILM_PIPELINE


class PipelineService:
    """Creates the initial dependency-aware job graph for one isolated film."""

    def __init__(self, session: AsyncSession) -> None:
        self.jobs = PostgresJobRepository(session)

    async def start(self, film_id: UUID, environment_id: UUID, payload: dict | None = None) -> list[object]:
        payload = payload or {}
        created = []
        for stage in FILM_PIPELINE:
            created.append(
                await self.jobs.create(
                    film_id=film_id,
                    environment_id=environment_id,
                    job_type=stage.name,
                    payload={"film": payload, "depends_on": list(stage.depends_on)},
                )
            )
        return created
