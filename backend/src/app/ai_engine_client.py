from __future__ import annotations

import os
from typing import Any
from uuid import UUID

import httpx


class AIEngineError(RuntimeError):
    pass


class AIEngineClient:
    """Backend-to-AI-engine transport boundary.

    The control plane never imports heavy ML dependencies. It sends a film-scoped
    job to the dedicated AI worker service and receives a JSON execution result.
    """

    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = (base_url or os.getenv("AI_ENGINE_URL", "http://ai-engine:8080")).rstrip("/")
        self.timeout = timeout or float(os.getenv("AI_ENGINE_TIMEOUT_SECONDS", "300"))

    async def execute_job(self, *, job_id: UUID, client_id: UUID, film_id: UUID, operation: str, payload: dict[str, Any], environment_id: UUID) -> dict[str, Any]:
        request = {
            "job_id": str(job_id),
            "client_id": str(client_id),
            "film_id": str(film_id),
            "environment_id": str(environment_id),
            "operation": operation,
            "payload": payload,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/v1/jobs/execute", json=request)
        except httpx.HTTPError as exc:
            raise AIEngineError(f"AI engine unavailable: {exc}") from exc
        if response.status_code >= 400:
            raise AIEngineError(f"AI engine rejected job ({response.status_code}): {response.text[:500]}")
        data = response.json()
        if not isinstance(data, dict):
            raise AIEngineError("AI engine returned an invalid response")
        return data

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/health")
            return response.is_success
        except httpx.HTTPError:
            return False
