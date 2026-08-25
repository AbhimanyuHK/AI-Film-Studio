from typing import Protocol
from uuid import UUID

from app.repository import ClientRecord, FilmRecord


class Repository(Protocol):
    async def create_client(self, name: str) -> ClientRecord: ...

    async def get_client(self, client_id: UUID) -> ClientRecord | None: ...

    async def create_film(
        self,
        client_id: UUID,
        name: str,
        source_language: str,
        target_languages: list[str],
    ) -> FilmRecord: ...

    async def get_film(self, film_id: UUID) -> FilmRecord | None: ...

    async def list_films_for_client(self, client_id: UUID) -> list[FilmRecord]: ...

    async def write_audit_event(
        self,
        *,
        actor_id: str,
        action: str,
        outcome: str,
        client_id: UUID | None = None,
        film_id: UUID | None = None,
        environment_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> None: ...
