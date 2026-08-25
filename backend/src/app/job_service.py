from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.job_repository import PostgresJobRepository


ALLOWED_JOB_TYPES = {
    "script_analysis",
    "character_generation",
    "environment_generation",
    "storyboard",
    "shot_generation",
    "video_generation",
    "voice_generation",
    "translation",
    "dubbing",
    "music_generation",
    "sfx_generation",
    "editing",
    "upscaling",
    "final_render",
}


class JobService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = PostgresJobRepository(session)

    async def enqueue(self, film_id: UUID, environment_id: UUID, job_type: str, payload: dict) -> object:
        if job_type not in ALLOWED_JOB_TYPES:
            raise ValueError(f"Unsupported job type: {job_type}")
        return await self.repository.create(film_id, environment_id, job_type, payload)
