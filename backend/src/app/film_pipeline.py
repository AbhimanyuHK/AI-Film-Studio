from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.pipeline_graph import PipelineGraphService


@dataclass(frozen=True)
class ProductionRun:
    film_id: UUID
    environment_id: UUID
    job_ids: list[UUID]


class FilmProductionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.graph = PipelineGraphService()

    async def start(self, film_id: UUID, environment_id: UUID, payload: dict | None = None) -> ProductionRun:
        job_ids = await self.graph.create_graph(self.session, film_id, environment_id, payload)
        await self.session.commit()
        return ProductionRun(film_id, environment_id, job_ids)
