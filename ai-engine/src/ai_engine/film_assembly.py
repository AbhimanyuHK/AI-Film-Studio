from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class FilmRenderer(Protocol):
    def render(self, shots: list[Any], audio: Any = None, subtitles: str | None = None, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class FilmAssemblyRequest:
    film_id: str
    language: str
    shot_outputs: tuple[Any, ...]
    audio: Any
    subtitles_srt: str
    fps: int = 24
    width: int = 1920
    height: int = 1080


@dataclass(frozen=True)
class FilmAssemblyResult:
    film_id: str
    language: str
    master: Any


class FilmAssembler:
    """Provider-neutral final render boundary; all inputs are explicitly film-scoped."""

    def __init__(self, renderer: FilmRenderer) -> None:
        self.renderer = renderer

    def assemble(self, request: FilmAssemblyRequest) -> FilmAssemblyResult:
        if not request.film_id or not request.language:
            raise ValueError("film_id and language are required")
        if not request.shot_outputs:
            raise ValueError("at least one shot output is required")
        if request.fps < 1 or request.width < 256 or request.height < 256:
            raise ValueError("invalid output dimensions or fps")
        master = self.renderer.render(
            list(request.shot_outputs),
            audio=request.audio,
            subtitles=request.subtitles_srt,
            fps=request.fps,
            width=request.width,
            height=request.height,
            film_id=request.film_id,
            language=request.language,
        )
        return FilmAssemblyResult(request.film_id, request.language, master)
