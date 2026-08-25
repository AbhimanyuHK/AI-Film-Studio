from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .shot_prompts import build_shot_prompt
from .storyboard import Shot


class ImagePipeline(Protocol):
    def generate(self, prompt: str, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class ImageGenerationRequest:
    film_id: str
    shot_id: str
    model: str
    prompt: str
    width: int = 1024
    height: int = 1024
    steps: int = 30
    guidance_scale: float = 3.5
    seed: int | None = None


@dataclass(frozen=True)
class ImageGenerationResult:
    film_id: str
    shot_id: str
    model: str
    output: Any


def build_image_request(film_id: str, shot: Shot, model: str = "FLUX.1-dev", **kwargs: Any) -> ImageGenerationRequest:
    return ImageGenerationRequest(
        film_id=film_id,
        shot_id=shot.shot_id,
        model=model,
        prompt=build_shot_prompt(shot),
        **kwargs,
    )


class ImageGenerator:
    """Runs an already-loaded image pipeline; model loading stays in ModelManager."""

    def __init__(self, pipeline: ImagePipeline) -> None:
        self.pipeline = pipeline

    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        if not request.film_id or not request.shot_id:
            raise ValueError("film_id and shot_id are required")
        if request.width < 256 or request.height < 256:
            raise ValueError("image dimensions must be at least 256px")
        if request.steps < 1:
            raise ValueError("steps must be positive")
        kwargs: dict[str, Any] = {
            "width": request.width,
            "height": request.height,
            "num_inference_steps": request.steps,
            "guidance_scale": request.guidance_scale,
        }
        if request.seed is not None:
            kwargs["seed"] = request.seed
        output = self.pipeline.generate(request.prompt, **kwargs)
        return ImageGenerationResult(request.film_id, request.shot_id, request.model, output)
