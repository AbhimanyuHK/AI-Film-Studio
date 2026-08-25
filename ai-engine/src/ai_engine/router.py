from typing import Any

from .contracts import FilmJob, GenerationResult, ModelAdapter


class ModelRouter:
    """Routes each film job to a configured model adapter."""

    def __init__(self) -> None:
        self._adapters: dict[str, ModelAdapter] = {}

    def register(self, job_type: str, adapter: ModelAdapter) -> None:
        self._adapters[job_type] = adapter

    def resolve(self, job_type: str) -> ModelAdapter:
        try:
            return self._adapters[job_type]
        except KeyError as exc:
            raise LookupError(f"No model adapter registered for {job_type}") from exc

    async def execute(self, job: FilmJob) -> GenerationResult:
        return await self.resolve(job.job_type).generate(job)
