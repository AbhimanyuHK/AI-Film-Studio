from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class FilmJob:
    job_id: UUID
    film_id: UUID
    environment_id: UUID
    job_type: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Artifact:
    asset_type: str
    filename: str
    content_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationResult:
    artifacts: tuple[Artifact, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelAdapter:
    """Contract implemented by each concrete open-model worker."""

    name = "base"

    async def generate(self, job: FilmJob) -> GenerationResult:
        raise NotImplementedError
