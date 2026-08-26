from __future__ import annotations

from typing import Any


def build_integration_executor():
    """Deterministic executor for local/CI integration.

    Production deployments must replace this with a real provider-backed
    executor through AI_EXECUTOR_FACTORY. This implementation intentionally
    produces metadata only and never pretends to generate media.
    """

    def execute(request: Any) -> dict[str, Any]:
        payload = request.payload if isinstance(request.payload, dict) else {}
        return {
            "mode": "integration",
            "operation": request.operation,
            "job_id": request.job_id,
            "client_id": request.client_id,
            "film_id": request.film_id,
            "environment_id": request.environment_id,
            "accepted": True,
            "payload_keys": sorted(payload.keys()),
        }

    return execute
