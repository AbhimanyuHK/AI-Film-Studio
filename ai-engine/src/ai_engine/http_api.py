from __future__ import annotations

import importlib
import os
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class JobExecutionRequest(BaseModel):
    job_id: str
    client_id: str
    film_id: str
    environment_id: str
    operation: str
    payload: dict[str, Any] = Field(default_factory=dict)


class JobExecutionResponse(BaseModel):
    job_id: str
    status: str
    result: dict[str, Any] = Field(default_factory=dict)


def _load_executor() -> Callable[[JobExecutionRequest], Any]:
    target = os.getenv("AI_EXECUTOR_FACTORY")
    if not target or ":" not in target:
        raise RuntimeError("AI_EXECUTOR_FACTORY must be configured as module:function")
    module_name, function_name = target.split(":", 1)
    factory = getattr(importlib.import_module(module_name), function_name)
    executor = factory()
    if not callable(executor):
        raise TypeError("AI_EXECUTOR_FACTORY must return a callable")
    return executor


app = FastAPI(title="AI Film Studio AI Engine", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/jobs/execute", response_model=JobExecutionResponse)
def execute_job(request: JobExecutionRequest) -> JobExecutionResponse:
    if not request.job_id or not request.client_id or not request.film_id or not request.environment_id:
        raise HTTPException(status_code=422, detail="job_id, client_id, film_id and environment_id are required")
    if not request.operation:
        raise HTTPException(status_code=422, detail="operation is required")
    try:
        result = _load_executor()(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI execution failed: {type(exc).__name__}: {exc}") from exc
    if result is None:
        result = {}
    if not isinstance(result, dict):
        result = {"value": result}
    return JobExecutionResponse(job_id=request.job_id, status="completed", result=result)
