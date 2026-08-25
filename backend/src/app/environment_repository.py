from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DeploymentModel, FilmEnvironmentModel


class PostgresEnvironmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_environment_by_film(self, film_id: UUID) -> FilmEnvironmentModel | None:
        result = await self.session.execute(
            select(FilmEnvironmentModel).where(FilmEnvironmentModel.film_id == film_id)
        )
        return result.scalar_one_or_none()

    async def get_environment(self, environment_id: UUID) -> FilmEnvironmentModel | None:
        return await self.session.get(FilmEnvironmentModel, environment_id)

    async def create_environment(
        self,
        *,
        film_id: UUID,
        aws_account_id: str,
        aws_region: str,
        subdomain: str,
    ) -> FilmEnvironmentModel:
        record = FilmEnvironmentModel(
            environment_id=uuid4(),
            film_id=film_id,
            provider="aws",
            aws_account_id=aws_account_id,
            aws_region=aws_region,
            subdomain=subdomain,
            terraform_state_key=f"films/{film_id}/environment.tfstate",
            status="provisioning",
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def create_deployment(self, environment_id: UUID, version: str) -> DeploymentModel:
        record = DeploymentModel(
            deployment_id=uuid4(),
            environment_id=environment_id,
            version=version,
            status="queued",
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_deployment(self, deployment_id: UUID) -> DeploymentModel | None:
        return await self.session.get(DeploymentModel, deployment_id)
