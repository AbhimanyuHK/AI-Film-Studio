from __future__ import annotations

# Canonical language identifiers for the studio's multilingual release pipeline.
SUPPORTED_LANGUAGES: tuple[str, ...] = (
    "en-US", "en-GB", "hi", "kn", "ta", "te", "ml", "bn", "mr", "gu",
    "zh-CN", "ja", "fr",
)


def validate_language(language: str) -> str:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"unsupported studio language: {language}")
    return language
