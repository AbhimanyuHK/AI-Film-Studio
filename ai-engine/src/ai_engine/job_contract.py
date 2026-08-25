from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class JobOperation(str, Enum):
    STORY_ANALYSIS = "story_analysis"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    LIP_SYNC = "lip_sync"
    FILM_ASSEMBLY = "film_assembly"


@dataclass(frozen=True)
class AIJob:
    job_id: str
    client_id: str
    film_id: str
    operation: JobOperation
    payload: dict[str, object] = field(default_factory=dict)
    parent_job_id: str | None = None
    attempt: int = 1

    @classmethod
    def create(cls, client_id: str, film_id: str, operation: JobOperation, payload: dict[str, object] | None = None, parent_job_id: str | None = None) -> "AIJob":
        if not client_id or not film_id:
            raise ValueError("client_id and film_id are required")
        return cls(uuid4().hex, client_id, film_id, operation, payload or {}, parent_job_id)

    def child(self, operation: JobOperation, payload: dict[str, object] | None = None) -> "AIJob":
        return AIJob.create(self.client_id, self.film_id, operation, payload, parent_job_id=self.job_id)
