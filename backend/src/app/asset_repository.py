from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.asset_models import AssetModel


class PostgresAssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, film_id: UUID, environment_id: UUID, object_key: str, asset_type: str, content_type: str, metadata: dict | None = None) -> AssetModel:
        asset = AssetModel(asset_id=uuid4(), film_id=film_id, environment_id=environment_id, object_key=object_key, asset_type=asset_type, content_type=content_type, metadata=metadata or {})
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def get(self, asset_id: UUID) -> AssetModel | None:
        return await self.session.get(AssetModel, asset_id)

    async def list_for_film(self, film_id: UUID) -> list[AssetModel]:
        result = await self.session.execute(select(AssetModel).where(AssetModel.film_id == film_id).order_by(AssetModel.created_at))
        return list(result.scalars().all())
