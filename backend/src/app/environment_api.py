from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api import _films

router = APIRouter(prefix="/api/v1", tags=["environments"])


class EnvironmentCreate(BaseModel):
    aws_account_id: str = Field(min_length=12, max_length=20)
    aws_region: str = Field(min_length=5, max_length=32)
    subdomain: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")


class Environment(BaseModel):
    environment_id: UUID
    film_id: UUID
    provider: str = "aws"
    aws_account_id: str
    aws_region: str
    subdomain: str
    status: str = "provisioning"


class DeploymentCreate(BaseModel):
    version: str = Field(min_length=1, max_length=100)


class Deployment(BaseModel):
    deployment_id: UUID
    environment_id: UUID
    version: str
    status: str = "queued"


_environments: dict[UUID, Environment] = {}
_film_environment: dict[UUID, UUID] = {}
_deployments: dict[UUID, Deployment] = {}


@router.post("/films/{film_id}/environment", response_model=Environment, status_code=status.HTTP_201_CREATED)
def create_environment(film_id: UUID, payload: EnvironmentCreate) -> Environment:
    if film_id not in _films:
        raise HTTPException(status_code=404, detail="Film not found")
    if film_id in _film_environment:
        raise HTTPException(status_code=409, detail="Film already has an environment")
    if any(env.subdomain == payload.subdomain for env in _environments.values()):
        raise HTTPException(status_code=409, detail="Subdomain already exists")

    environment = Environment(
        environment_id=uuid4(),
        film_id=film_id,
        aws_account_id=payload.aws_account_id,
        aws_region=payload.aws_region,
        subdomain=payload.subdomain,
    )
    _environments[environment.environment_id] = environment
    _film_environment[film_id] = environment.environment_id
    return environment


@router.get("/films/{film_id}/environment", response_model=Environment)
def get_environment(film_id: UUID) -> Environment:
    environment_id = _film_environment.get(film_id)
    if environment_id is None:
        raise HTTPException(status_code=404, detail="Environment not found")
    return _environments[environment_id]


@router.post("/films/{film_id}/deployments", response_model=Deployment, status_code=status.HTTP_201_CREATED)
def create_deployment(film_id: UUID, payload: DeploymentCreate) -> Deployment:
    environment_id = _film_environment.get(film_id)
    if environment_id is None:
        raise HTTPException(status_code=404, detail="Environment not found")

    deployment = Deployment(
        deployment_id=uuid4(),
        environment_id=environment_id,
        version=payload.version,
    )
    _deployments[deployment.deployment_id] = deployment
    return deployment


@router.get("/deployments/{deployment_id}", response_model=Deployment)
def get_deployment(deployment_id: UUID) -> Deployment:
    deployment = _deployments.get(deployment_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment
