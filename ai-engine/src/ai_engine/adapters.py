from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


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
    output_assets: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None


class ModelAdapter(ABC):
    name: str
    stages: tuple[str, ...]

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        raise NotImplementedError


class ScriptAnalysisAdapter(ModelAdapter):
    name = "script-analysis"
    stages = ("script_analysis",)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        # Provider integration is deliberately injected later; this contract
        # keeps prompts/assets isolated per film and provider-independent.
        return GenerationResult(status="completed", metadata={"stage": request.stage})


class ImageGenerationAdapter(ModelAdapter):
    name = "image-generation"
    stages = ("character_generation", "environment_generation", "storyboard")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(status="completed", metadata={"stage": request.stage})


class VideoGenerationAdapter(ModelAdapter):
    name = "video-generation"
    stages = ("shot_generation", "video_generation")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(status="completed", metadata={"stage": request.stage})


class AudioGenerationAdapter(ModelAdapter):
    name = "audio-generation"
    stages = ("voice_generation", "translation", "dubbing", "music_generation", "sfx_generation")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(status="completed", metadata={"stage": request.stage})
