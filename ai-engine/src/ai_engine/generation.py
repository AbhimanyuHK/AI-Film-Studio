from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model_config import ModelSpec
from .model_manager import ModelManager


@dataclass(frozen=True)
class GenerationOutput:
    model: str
    stage: str
    status: str
    payload: dict[str, Any]


class GenerationEngine:
    def __init__(self, manager: ModelManager | None = None) -> None:
        self.manager = manager or ModelManager()

    async def execute(self, model: ModelSpec, stage: str, inputs: dict[str, Any], parameters: dict[str, Any] | None = None) -> GenerationOutput:
        loaded = self.manager.load(model.name, model.backend)
        # Backend-specific inference is intentionally delegated to the loaded pipeline.
        # This method defines the common result contract; stage adapters own prompt/image/video semantics.
        return GenerationOutput(
            model=loaded.name,
            stage=stage,
            status="loaded",
            payload={"input_keys": tuple(inputs.keys()), "parameters": parameters or {}, "device": loaded.device},
        )
