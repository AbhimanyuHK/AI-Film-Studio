from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model_config import ModelSpec, models_for_stage


@dataclass(frozen=True)
class RuntimeRequest:
    stage: str
    model: str | None = None
    device: str = "cuda"
    parameters: dict[str, Any] | None = None


class ModelRuntime:
    """GPU runtime boundary. Actual inference engines plug in behind this API."""

    def select_model(self, request: RuntimeRequest) -> ModelSpec:
        candidates = models_for_stage(request.stage)
        if request.model:
            candidates = tuple(m for m in candidates if m.name == request.model)
        if not candidates:
            raise LookupError(f"No configured model for stage={request.stage}, model={request.model}")
        return candidates[0]

    async def generate(self, request: RuntimeRequest, inputs: dict[str, Any]) -> dict[str, Any]:
        model = self.select_model(request)
        return {
            "status": "accepted",
            "stage": request.stage,
            "model": model.name,
            "backend": model.backend,
            "device": request.device,
            "inputs": tuple(inputs.keys()),
        }
