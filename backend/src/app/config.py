from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str | None = os.getenv("DATABASE_URL")
    environment: str = os.getenv("APP_ENV", "development")
    auth_mode: str = os.getenv("AUTH_MODE", "development")
    jwt_secret: str | None = os.getenv("JWT_SECRET")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_issuer: str | None = os.getenv("JWT_ISSUER")
    jwt_audience: str | None = os.getenv("JWT_AUDIENCE")


settings = Settings()

if settings.auth_mode == "production":
    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must be configured with at least 32 characters in production")
    if settings.jwt_algorithm != "HS256":
        raise RuntimeError("Only HS256 is currently supported by the built-in JWT verifier")
