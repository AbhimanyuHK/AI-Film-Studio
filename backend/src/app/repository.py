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
    """Repository interface implementation used until the Postgres adapter lands."""

    def __init__(self) -> None:
        self.clients: dict[UUID, ClientRecord] = {}
        self.films: dict[UUID, FilmRecord] = {}

    def create_client(self, name: str) -> ClientRecord:
        record = ClientRecord(client_id=uuid4(), name=name)
        self.clients[record.client_id] = record
        return record

    def get_client(self, client_id: UUID) -> ClientRecord | None:
        return self.clients.get(client_id)

    def create_film(
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

    def get_film(self, film_id: UUID) -> FilmRecord | None:
        return self.films.get(film_id)
