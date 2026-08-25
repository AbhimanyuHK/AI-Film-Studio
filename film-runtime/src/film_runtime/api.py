from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import get_db
from .executor import FilmRuntimeExecutor
from .rag import FilmKnowledgeIndex, KnowledgeChunk
from .scope import enforce_scope

app = FastAPI(title='AI Film Studio Film Runtime', version='1.0.0')
knowledge = FilmKnowledgeIndex()


class ExecuteRequest(BaseModel):
    job_id: str
    operation: str
    payload: dict[str, Any] = Field(default_factory=dict)


class KnowledgeRequest(BaseModel):
    chunk_id: str
    text: str
    source: str


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok', 'film_id': settings.runtime_film_id}


@app.get('/v1/scope')
async def scope(_: None = Depends(enforce_scope)) -> dict[str, str]:
    return {'client_id': settings.runtime_client_id, 'film_id': settings.runtime_film_id, 'environment_id': settings.runtime_environment_id}


@app.post('/v1/jobs/execute')
async def execute(request: ExecuteRequest, _: None = Depends(enforce_scope), session: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    try:
        result = await FilmRuntimeExecutor(session, knowledge).execute(job_id=request.job_id, operation=request.operation, payload=request.payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {'job_id': request.job_id, 'status': 'completed', 'result': result}


@app.post('/v1/knowledge')
async def add_knowledge(request: KnowledgeRequest, _: None = Depends(enforce_scope)) -> dict[str, str]:
    knowledge.upsert(KnowledgeChunk(request.chunk_id, request.text, request.source))
    return {'status': 'indexed', 'chunk_id': request.chunk_id}


@app.get('/v1/knowledge/search')
async def search_knowledge(q: str, limit: int = 8, _: None = Depends(enforce_scope)) -> dict[str, Any]:
    results = knowledge.search(q, min(max(limit, 1), 20))
    return {'results': [r.__dict__ for r in results]}
