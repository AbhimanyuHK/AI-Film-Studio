from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.auth import Principal, get_principal
from app.db import get_db
from app.postgres_repository import PostgresRepository
from app.environment_repository import PostgresEnvironmentRepository

router = APIRouter(prefix="/api/v1", tags=["environments"])


class EnvironmentCreate(BaseModel):
    aws_account_id: str = Field(min_length=12, max_length=20)
    aws_region: str = Field(min_length=5, max_length=32)
    subdomain: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")


class Environment(BaseModel):
    environment_id: UUID
    film_id: UUID
    provider: str
    aws_account_id: str
    aws_region: str
    subdomain: str
    status: str


class DeploymentCreate(BaseModel):
    version: str = Field(min_length=1, max_length=100)


class Deployment(BaseModel):
    deployment_id: UUID
    environment_id: UUID
    version: str
    status: str


def _authorize(principal: Principal, client_id: UUID) -> None:
    if principal.role != "platform_admin" and principal.client_id != str(client_id):
        raise HTTPException(status_code=403, detail="Cross-client access denied")


async def _film_or_404(session: AsyncSession, film_id: UUID):
    film = await session.get(type("Film", (), {}), film_id)  # replaced below by repository lookup
    return film


@router.post("/films/{film_id}/environment", response_model=Environment, status_code=status.HTTP_201_CREATED)
async def create_environment(
    film_id: UUID,
    payload: EnvironmentCreate,
    principal: Principal = Depends(get_principal),
    session: AsyncSession = Depends(get_db),
) -> Environment:
    films = PostgresRepository(session)
    film = await films.get_film(film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    _authorize(principal, film.client_id)

    repo = PostgresEnvironmentRepository(session)
    if await repo.get_environment_by_film(film_id):
        raise HTTPException(status_code=409, detail="Film already has an environment")

    try:
        record = await repo.create_environment(
            film_id=film_id,
            aws_account_id=payload.aws_account_id,
            aws_region=payload.aws_region,
            subdomain=payload.subdomain,
        )
        await repo.session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Environment already exists or subdomain is already in use")

    return Environment(
        environment_id=record.environment_id,
        film_id=record.film_id,
        provider=record.provider,
        aws_account_id=record.aws_account_id,
        aws_region=record.aws_region,
        subdomain=record.subdomain,
        status=record.status,
    )


@router.get("/films/{film_id}/environment", response_model=Environment)
async def get_environment(
    film_id: UUID,
    principal: Principal = Depends(get_principal),
    session: AsyncSession = Depends(get_db),
) -> Environment:
    films = PostgresRepository(session)
    film = await films.get_film(film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    _authorize(principal, film.client_id)

    record = await PostgresEnvironmentRepository(session).get_environment_by_film(film_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    return Environment(
        environment_id=record.environment_id,
        film_id=record.film_id,
        provider=record.provider,
        aws_account_id=record.aws_account_id,
        aws_region=record.aws_region,
        subdomain=record.subdomain,
        status=record.status,
    )


@router.post("/films/{film_id}/deployments", response_model=Deployment, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    film_id: UUID,
    payload: DeploymentCreate,
    principal: Principal = Depends(get_principal),
    session: AsyncSession = Depends(get_db),
) -> Deployment:
    films = PostgresRepository(session)
    film = await films.get_film(film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    _authorize(principal, film.client_id)

    repo = PostgresEnvironmentRepository(session)
    environment = await repo.get_environment_by_film(film_id)
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    record = await repo.create_deployment(environment.environment_id, payload.version)
    await session.commit()
    return Deployment(
        deployment_id=record.deployment_id,
        environment_id=record.environment_id,
        version=record.version,
        status=record.status,
    )


@router.get("/deployments/{deployment_id}", response_model=Deployment)
async def get_deployment(
    deployment_id: UUID,
    principal: Principal = Depends(get_principal),
    session: AsyncSession = Depends(get_db),
) -> Deployment:
    repo = PostgresEnvironmentRepository(session)
    record = await repo.get_deployment(deployment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Deployment not found")

    environment = await repo.get_environment(record.environment_id)
    if environment is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    film = await PostgresRepository(session).get_film(environment.film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    _authorize(principal, film.client_id)

    return Deployment(
        deployment_id=record.deployment_id,
        environment_id=record.environment_id,
        version=record.version,
        status=record.status,
    )
