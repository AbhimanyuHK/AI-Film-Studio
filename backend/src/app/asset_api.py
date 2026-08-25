from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import Principal, get_principal
from app.db import get_db
from app.asset_repository import PostgresAssetRepository
from app.environment_repository import PostgresEnvironmentRepository
from app.postgres_repository import PostgresRepository
from app.storage import FilmStorage

router = APIRouter(prefix="/api/v1", tags=["assets"])


class AssetCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    asset_type: str = Field(min_length=1, max_length=64)
    content_type: str = Field(min_length=1, max_length=255)
    metadata: dict = Field(default_factory=dict)


class AssetResponse(BaseModel):
    asset_id: UUID
    film_id: UUID
    asset_type: str
    content_type: str
    object_key: str
    status: str
    upload_url: str


def _authorize(principal: Principal, client_id: UUID) -> None:
    if principal.role != "platform_admin" and principal.client_id != str(client_id):
        raise HTTPException(status_code=403, detail="Cross-client access denied")


async def _film_and_environment(session: AsyncSession, film_id: UUID, principal: Principal):
    film = await PostgresRepository(session).get_film(film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    _authorize(principal, film.client_id)
    environment = await PostgresEnvironmentRepository(session).get_environment_by_film(film_id)
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    return film, environment


@router.post("/films/{film_id}/assets", response_model=AssetResponse, status_code=201)
async def create_asset(film_id: UUID, payload: AssetCreate, principal: Principal = Depends(get_principal), session: AsyncSession = Depends(get_db)):
    _, environment = await _film_and_environment(session, film_id, principal)
    storage = FilmStorage()
    key = storage.object_key(film_id, payload.asset_type, payload.filename)
    asset = await PostgresAssetRepository(session).create(film_id, environment.environment_id, key, payload.asset_type, payload.content_type, payload.metadata)
    await session.commit()
    return AssetResponse(asset_id=asset.asset_id, film_id=film_id, asset_type=asset.asset_type, content_type=asset.content_type, object_key=asset.object_key, status=asset.status, upload_url=storage.presigned_upload(key, payload.content_type))


@router.get("/films/{film_id}/assets", response_model=list[AssetResponse])
async def list_assets(film_id: UUID, principal: Principal = Depends(get_principal), session: AsyncSession = Depends(get_db)):
    await _film_and_environment(session, film_id, principal)
    storage = FilmStorage()
    assets = await PostgresAssetRepository(session).list_for_film(film_id)
    return [AssetResponse(asset_id=a.asset_id, film_id=a.film_id, asset_type=a.asset_type, content_type=a.content_type, object_key=a.object_key, status=a.status, upload_url=storage.presigned_download(a.object_key)) for a in assets]
