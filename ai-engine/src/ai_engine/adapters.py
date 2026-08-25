from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from .configured_runtime import ConfiguredRuntime
from .model_config import models_for_stage

@dataclass(frozen=True)
class GenerationRequest:
    job_id: str
    film_id: str
    stage: str
    prompt: str
    input_assets: tuple[str, ...] = ()
    parameters: dict[str, Any] | None = None

@dataclass(frozen=True)
class GenerationResult:
    status: str
    output_assets: tuple[bytes, ...] = ()
    metadata: dict[str, Any] | None = None

class ModelAdapter(ABC):
    name: str
    stages: tuple[str, ...]
    def __init__(self, runtime: ConfiguredRuntime | None = None) -> None:
        self.runtime = runtime
    def _runtime(self) -> ConfiguredRuntime:
        if self.runtime is None:
            self.runtime = ConfiguredRuntime()
        return self.runtime
    def _model(self, stage: str) -> str:
        models = models_for_stage(stage)
        if not models:
            raise RuntimeError(f"no model configured for stage: {stage}")
        return models[0].name
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...

class ScriptAnalysisAdapter(ModelAdapter):
    name = "script-analysis"
    stages = ("script_analysis",)
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        out = self._runtime().execute(request.stage, self._model(request.stage), request.prompt, request.parameters)
        return GenerationResult("completed", out.assets, {**out.metadata, "job_id": request.job_id, "film_id": request.film_id})

class ImageGenerationAdapter(ModelAdapter):
    name = "image-generation"
    stages = ("character_generation", "environment_generation", "storyboard", "storyboard_image")
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        out = self._runtime().execute(request.stage, self._model(request.stage), request.prompt, request.parameters)
        return GenerationResult("completed", out.assets, {**out.metadata, "job_id": request.job_id, "film_id": request.film_id})

class VideoGenerationAdapter(ModelAdapter):
    name = "video-generation"
    stages = ("shot_generation", "video_generation")
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        out = self._runtime().execute(request.stage, self._model(request.stage), request.prompt, request.parameters)
        return GenerationResult("completed", out.assets, {**out.metadata, "job_id": request.job_id, "film_id": request.film_id})

class AudioGenerationAdapter(ModelAdapter):
    name = "audio-generation"
    stages = ("voice_generation", "translation", "dubbing", "music_generation", "sfx_generation", "transcription")
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        model = self._model(request.stage) if models_for_stage(request.stage) else "configured-audio-provider"
        out = self._runtime().execute(request.stage, model, request.prompt, request.parameters)
        return GenerationResult("completed", out.assets, {**out.metadata, "job_id": request.job_id, "film_id": request.film_id})
