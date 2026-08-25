from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .adapters import GenerationRequest, GenerationResult
from .default_registry import adapter_for_stage

@dataclass(frozen=True)
class FilmGenerationResult:
    film_id: str
    stages: tuple[GenerationResult, ...]

class ProductionFilmPipeline:
    STAGES = ("script_analysis", "character_generation", "environment_generation", "storyboard_image", "shot_generation", "voice_generation", "translation", "dubbing", "music_generation", "sfx_generation")
    def __init__(self, adapters: dict[str, Any] | None = None) -> None:
        self.adapters = adapters or {}
    async def run(self, job_id: str, film_id: str, prompt: str, parameters: dict[str, Any] | None = None) -> FilmGenerationResult:
        if not job_id or not film_id or not prompt:
            raise ValueError("job_id, film_id and prompt are required")
        results = []
        context = prompt
        for index, stage in enumerate(self.STAGES, 1):
            adapter = self.adapters.get(stage) or adapter_for_stage(stage)
            result = await adapter.generate(GenerationRequest(f"{job_id}-{index}", film_id, stage, context, parameters=parameters))
            if result.status != "completed":
                raise RuntimeError(f"AI stage failed: {stage}")
            results.append(result)
            context += f"\nCompleted stage: {stage}."
        return FilmGenerationResult(film_id, tuple(results))
