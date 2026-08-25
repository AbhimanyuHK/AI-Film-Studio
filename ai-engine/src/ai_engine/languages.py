from dataclasses import dataclass


@dataclass(frozen=True)
class FilmLanguage:
    code: str
    name: str
    variant: str | None = None


SUPPORTED_LANGUAGES = (
    FilmLanguage("kn", "Kannada"),
    FilmLanguage("hi", "Hindi"),
    FilmLanguage("ta", "Tamil"),
    FilmLanguage("te", "Telugu"),
    FilmLanguage("ml", "Malayalam"),
    FilmLanguage("mr", "Marathi"),
    FilmLanguage("bn", "Bengali"),
    FilmLanguage("en", "English", "US"),
    FilmLanguage("en", "English", "UK"),
    FilmLanguage("zh", "Chinese", "Mandarin"),
    FilmLanguage("ja", "Japanese"),
    FilmLanguage("fr", "French"),
)


def language_key(language: FilmLanguage) -> str:
    return f"{language.code}-{language.variant.lower()}" if language.variant else language.code
