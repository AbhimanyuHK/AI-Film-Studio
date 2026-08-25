from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class LipSyncPipeline(Protocol):
    def synchronize(self, video: Any, audio: Any, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class LipSyncRequest:
    film_id: str
    shot_id: str
    language: str
    model: str = "lip-sync"
    sync_strength: float = 1.0


@dataclass(frozen=True)
class LipSyncResult:
    film_id: str
    shot_id: str
    language: str
    output: Any


class LipSyncGenerator:
    """Provider-neutral lip-sync boundary for the GPU worker."""

    def __init__(self, pipeline: LipSyncPipeline) -> None:
        self.pipeline = pipeline

    def generate(self, request: LipSyncRequest, video: Any, audio: Any) -> LipSyncResult:
        if not request.film_id or not request.shot_id:
            raise ValueError("film_id and shot_id are required")
        if not request.language:
            raise ValueError("language is required")
        if not 0.0 <= request.sync_strength <= 1.0:
            raise ValueError("sync_strength must be between 0 and 1")
        output = self.pipeline.synchronize(video, audio, sync_strength=request.sync_strength)
        return LipSyncResult(request.film_id, request.shot_id, request.language, output)
