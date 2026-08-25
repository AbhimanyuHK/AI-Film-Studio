from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class VideoPipeline(Protocol):
    def generate(self, image: Any, prompt: str, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class VideoGenerationRequest:
    film_id: str
    shot_id: str
    model: str = "HunyuanVideo"
    prompt: str = ""
    duration_seconds: float = 5.0
    fps: int = 24
    width: int = 1280
    height: int = 720
    seed: int | None = None


@dataclass(frozen=True)
class VideoGenerationResult:
    film_id: str
    shot_id: str
    model: str
    output: Any


class VideoGenerator:
    """Provider-neutral image-to-video execution boundary for GPU workers."""

    def __init__(self, pipeline: VideoPipeline) -> None:
        self.pipeline = pipeline

    def generate(self, request: VideoGenerationRequest, keyframe: Any) -> VideoGenerationResult:
        if not request.film_id or not request.shot_id:
            raise ValueError("film_id and shot_id are required")
        if request.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if request.fps < 1:
            raise ValueError("fps must be positive")
        if request.width < 256 or request.height < 256:
            raise ValueError("video dimensions must be at least 256px")
        output = self.pipeline.generate(keyframe, request.prompt, duration_seconds=request.duration_seconds, fps=request.fps, width=request.width, height=request.height, seed=request.seed)
        return VideoGenerationResult(request.film_id, request.shot_id, request.model, output)
