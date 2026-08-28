from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ClientRecord:
    client_id: UUID
    name: str
    status: str = "active"


@dataclass(frozen=True)
class FilmRecord:
    film_id: UUID
    client_id: UUID
    name: str
    source_language: str
    target_languages: tuple[str, ...]
    status: str = "draft"


class InMemoryRepository:
    """Async repository implementation for local/unit-test execution."""

    def __init__(self) -> None:
        self.clients: dict[UUID, ClientRecord] = {}
        self.films: dict[UUID, FilmRecord] = {}

    async def create_client(self, name: str) -> ClientRecord:
        record = ClientRecord(client_id=uuid4(), name=name)
        self.clients[record.client_id] = record
        return record

    async def get_client(self, client_id: UUID) -> ClientRecord | None:
        return self.clients.get(client_id)

    async def create_film(
        self,
        client_id: UUID,
        name: str,
        source_language: str,
        target_languages: list[str],
    ) -> FilmRecord:
        record = FilmRecord(
            film_id=uuid4(),
            client_id=client_id,
            name=name,
            source_language=source_language,
            target_languages=tuple(target_languages),
        )
        self.films[record.film_id] = record
        return record

    async def get_film(self, film_id: UUID) -> FilmRecord | None:
        return self.films.get(film_id)

    async def list_films_for_client(self, client_id: UUID) -> list[FilmRecord]:
        return [film for film in self.films.values() if film.client_id == client_id]

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
    ) -> None:
        # Audit persistence is intentionally a no-op for in-memory test execution.
        return None
