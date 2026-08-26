from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_engine_client import AIEngineClient
from app.auth import Principal, get_principal
from app.db import get_db
from app.environment_repository import PostgresEnvironmentRepository
from app.job_repository import PostgresJobRepository
from app.pipeline_graph import PipelineGraphService
from app.pipeline import FILM_PIPELINE
from app.postgres_repository import PostgresRepository

router = APIRouter(prefix="/api/v1", tags=["production"])


class StartProductionRequest(BaseModel):
    payload: dict = Field(default_factory=dict)


class EnqueueJobRequest(BaseModel):
    job_type: str
    payload: dict = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=200)
    max_attempts: int = Field(default=3, ge=1, le=10)


def _authorize(principal: Principal, film_client_id: UUID) -> None:
    if principal.role == "platform_admin":
        return
    if principal.client_id != str(film_client_id):
        raise HTTPException(status_code=403, detail="Cross-client access denied")


async def _film_context(session: AsyncSession, film_id: UUID, principal: Principal):
    from app.models import FilmModel

    film = await session.get(FilmModel, film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    _authorize(principal, film.client_id)
    environment = await PostgresEnvironmentRepository(session).get_environment_by_film(film_id)
    if environment is None:
        raise HTTPException(status_code=409, detail="Film environment is not provisioned")
    return film, environment


@router.post("/films/{film_id}/production/start", status_code=status.HTTP_202_ACCEPTED)
async def start_production(
    film_id: UUID,
    request: StartProductionRequest,
    principal: Principal = Depends(get_principal),
    session: AsyncSession = Depends(get_db),
):
    _, environment = await _film_context(session, film_id, principal)
    job_ids = await PipelineGraphService().create_graph(session, film_id, environment.environment_id, request.payload)
    await session.commit()
    return {"film_id": film_id, "environment_id": environment.environment_id, "status": "queued", "job_ids": job_ids}


@router.post("/films/{film_id}/jobs", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_job(
    film_id: UUID,
    request: EnqueueJobRequest,
    principal: Principal = Depends(get_principal),
    session: AsyncSession = Depends(get_db),
):
    film, environment = await _film_context(session, film_id, principal)
    allowed = {stage.name for stage in FILM_PIPELINE}
    if request.job_type not in allowed:
        raise HTTPException(status_code=422, detail="Unsupported production job type")
    job = await PostgresJobRepository(session).create(
        film_id,
        environment.environment_id,
        request.job_type,
        request.payload,
        max_attempts=request.max_attempts,
        idempotency_key=request.idempotency_key,
    )
    await PostgresRepository(session).write_audit_event(
        actor_id=principal.subject,
        action="job.enqueue",
        outcome="success",
        client_id=film.client_id,
        film_id=film_id,
        environment_id=environment.environment_id,
        metadata={"job_id": str(job.job_id), "job_type": request.job_type},
    )
    await session.commit()
    return {"job_id": job.job_id, "film_id": film_id, "environment_id": environment.environment_id, "status": job.status}


@router.get("/films/{film_id}/jobs")
async def list_jobs(film_id: UUID, principal: Principal = Depends(get_principal), session: AsyncSession = Depends(get_db)):
    await _film_context(session, film_id, principal)
    jobs = await PostgresJobRepository(session).list_for_film(film_id)
    return [
        {
            "job_id": j.job_id,
            "job_type": j.job_type,
            "status": j.status,
            "attempts": j.attempts,
            "max_attempts": j.max_attempts,
            "error_code": j.error_code,
            "result": j.result,
        }
        for j in jobs
    ]


@router.get("/jobs/{job_id}")
async def get_job(job_id: UUID, principal: Principal = Depends(get_principal), session: AsyncSession = Depends(get_db)):
    job = await PostgresJobRepository(session).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    await _film_context(session, job.film_id, principal)
    return {
        "job_id": job.job_id,
        "film_id": job.film_id,
        "environment_id": job.environment_id,
        "job_type": job.job_type,
        "status": job.status,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
        "error_code": job.error_code,
        "result": job.result,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: UUID, principal: Principal = Depends(get_principal), session: AsyncSession = Depends(get_db)):
    job = await PostgresJobRepository(session).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    await _film_context(session, job.film_id, principal)
    await PostgresJobRepository(session).cancel(job)
    await session.commit()
    return {"job_id": job.job_id, "status": job.status}


@router.get("/ai-engine/health")
async def ai_engine_health(principal: Principal = Depends(get_principal)):
    del principal
    return {"status": "ok" if await AIEngineClient().health() else "unavailable"}
