from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceProfile:
    character_name: str
    language: str
    voice_id: str
    gender: str | None = None
    style: str = "cinematic"


class VoiceCatalog:
    """Film-scoped character voice mapping; no cross-film fallback."""

    def __init__(self) -> None:
        self._voices: dict[tuple[str, str, str], VoiceProfile] = {}

    def register(self, film_id: str, profile: VoiceProfile) -> VoiceProfile:
        if not film_id or not profile.character_name or not profile.voice_id:
            raise ValueError("film_id, character_name and voice_id are required")
        self._voices[(film_id, profile.character_name, profile.language)] = profile
        return profile

    def get(self, film_id: str, character_name: str, language: str) -> VoiceProfile | None:
        return self._voices.get((film_id, character_name, language))

    def require(self, film_id: str, character_name: str, language: str) -> VoiceProfile:
        profile = self.get(film_id, character_name, language)
        if profile is None:
            raise KeyError(f"no voice mapping for film={film_id!r}, character={character_name!r}, language={language!r}")
        return profile
