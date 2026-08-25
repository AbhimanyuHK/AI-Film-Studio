from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class InferenceBackend(Protocol):
    async def run(self, model: str, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class DiffusersBackend:
    device: str = "cuda"

    async def run(self, model: str, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        """Adapter boundary for Hugging Face Diffusers image/video pipelines.

        The heavyweight pipeline is intentionally created by the GPU worker
        process, not imported during API/test collection.
        """
        return {"backend": "diffusers", "model": model, "device": self.device, "status": "ready", "inputs": tuple(inputs), "parameters": parameters}


@dataclass
class VLLMBackend:
    endpoint: str | None = None

    async def run(self, model: str, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"backend": "vllm", "model": model, "endpoint": self.endpoint, "status": "ready", "inputs": tuple(inputs), "parameters": parameters}
