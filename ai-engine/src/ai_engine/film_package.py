from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FilmLanguagePackage:
    film_id: str
    language: str
    video: Any
    audio: Any
    subtitles_srt: str


class FilmPackageAssembler:
    """Builds a release package without mixing assets across films."""

    def assemble(self, film_id: str, language: str, video: Any, audio: Any, subtitles_srt: str) -> FilmLanguagePackage:
        if not film_id or not language:
            raise ValueError("film_id and language are required")
        return FilmLanguagePackage(film_id, language, video, audio, subtitles_srt)
