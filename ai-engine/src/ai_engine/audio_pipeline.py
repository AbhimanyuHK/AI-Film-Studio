from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

class Translator(Protocol):
    def translate(self, text: str, source_language: str, target_language: str) -> str: ...

class TextToSpeech(Protocol):
    def synthesize(self, text: str, language: str, voice_id: str, **kwargs: Any) -> Any: ...

@dataclass(frozen=True)
class DialogueSegment:
    character: str
    text: str
    start_seconds: float
    end_seconds: float

@dataclass(frozen=True)
class AudioGenerationRequest:
    film_id: str
    shot_id: str
    language: str
    voice_id: str
    segments: tuple[DialogueSegment, ...]
    source_language: str = "en"

@dataclass(frozen=True)
class AudioGenerationResult:
    film_id: str
    shot_id: str
    language: str
    audio: Any

class AudioPipeline:
    """Provider-neutral multilingual dialogue pipeline."""
    def __init__(self, tts: TextToSpeech, translator: Translator | None = None) -> None:
        self.tts = tts
        self.translator = translator

    def generate(self, request: AudioGenerationRequest) -> AudioGenerationResult:
        if not request.film_id or not request.shot_id:
            raise ValueError("film_id and shot_id are required")
        if not request.segments:
            raise ValueError("at least one dialogue segment is required")
        outputs: list[Any] = []
        for segment in request.segments:
            text = segment.text
            if request.language != request.source_language:
                if self.translator is None:
                    raise RuntimeError("translator is required for non-source-language dubbing")
                text = self.translator.translate(text, request.source_language, request.language)
            outputs.append(self.tts.synthesize(text, language=request.language, voice_id=request.voice_id, start_seconds=segment.start_seconds, end_seconds=segment.end_seconds, character=segment.character))
        return AudioGenerationResult(request.film_id, request.shot_id, request.language, outputs)
