from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str | None = os.getenv("DATABASE_URL")
    environment: str = os.getenv("APP_ENV", "development")
    auth_mode: str = os.getenv("AUTH_MODE", "development")


settings = Settings()
