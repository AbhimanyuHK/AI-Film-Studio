from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    runtime_client_id: str
    runtime_film_id: str
    runtime_environment_id: str
    runtime_shared_secret: str = ''
    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/film_runtime'
    s3_bucket: str = ''
    s3_prefix: str = ''
    aws_region: str = 'ap-south-1'
    ai_engine_url: str = 'http://ai-engine:8080'
    max_context_chars: int = 12000


settings = Settings()
