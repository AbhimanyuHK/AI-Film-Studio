from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .runtime import ModelRuntime, RuntimeRequest


@dataclass(frozen=True)
class WorkerResult:
    status: str
    model: str
    stage: str
    output: dict[str, Any]


class GPUWorker:
    """Execution boundary for a GPU worker process.

    Concrete inference engines (Diffusers, vLLM, ComfyUI, etc.) are injected
    behind ModelRuntime. The worker itself remains film/job scoped.
    """

    def __init__(self, runtime: ModelRuntime | None = None) -> None:
        self.runtime = runtime or ModelRuntime()

    async def execute(self, *, job_id: str, film_id: str, stage: str, inputs: dict[str, Any], model: str | None = None) -> WorkerResult:
        if not job_id or not film_id:
            raise ValueError("job_id and film_id are required")
        result = await self.runtime.generate(
            RuntimeRequest(stage=stage, model=model),
            inputs,
        )
        return WorkerResult(
            status=result["status"],
            model=result["model"],
            stage=stage,
            output={"job_id": job_id, "film_id": film_id, **result},
        )
