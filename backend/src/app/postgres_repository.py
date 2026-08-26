from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditEventModel, ClientModel, FilmModel
from app.repository import ClientRecord, FilmRecord


class PostgresRepository:
    """Persistent control-plane repository.

    Tenant authorization stays above this layer; callers must already have
    established the actor's access to the requested client/film.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_client(self, name: str) -> ClientRecord:
        record = ClientModel(client_id=uuid4(), name=name, status="active")
        self.session.add(record)
        await self.session.flush()
        return ClientRecord(record.client_id, record.name, record.status)

    async def get_client(self, client_id: UUID) -> ClientRecord | None:
        record = await self.session.get(ClientModel, client_id)
        if record is None:
            return None
        return ClientRecord(record.client_id, record.name, record.status)

    async def create_film(
        self,
        client_id: UUID,
        name: str,
        source_language: str,
        target_languages: list[str],
    ) -> FilmRecord:
        record = FilmModel(
            film_id=uuid4(),
            client_id=client_id,
            name=name,
            source_language=source_language,
            target_languages=target_languages,
            status="draft",
        )
        self.session.add(record)
        await self.session.flush()
        return FilmRecord(
            record.film_id,
            record.client_id,
            record.name,
            record.source_language,
            tuple(record.target_languages or []),
            record.status,
        )

    async def get_film(self, film_id: UUID) -> FilmRecord | None:
        record = await self.session.get(FilmModel, film_id)
        if record is None:
            return None
        return FilmRecord(
            record.film_id,
            record.client_id,
            record.name,
            record.source_language,
            tuple(record.target_languages or []),
            record.status,
        )

    async def list_films_for_client(self, client_id: UUID) -> list[FilmRecord]:
        result = await self.session.execute(
            select(FilmModel).where(FilmModel.client_id == client_id).order_by(FilmModel.created_at)
        )
        return [
            FilmRecord(
                row.film_id,
                row.client_id,
                row.name,
                row.source_language,
                tuple(row.target_languages or []),
                row.status,
            )
            for row in result.scalars().all()
        ]

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
        self.session.add(
            AuditEventModel(
                event_id=uuid4(),
                actor_id=actor_id,
                action=action,
                outcome=outcome,
                client_id=client_id,
                film_id=film_id,
                environment_id=environment_id,
                metadata_json=metadata or {},
            )
        )
        await self.session.flush()
