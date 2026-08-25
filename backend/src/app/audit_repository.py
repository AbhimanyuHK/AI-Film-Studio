from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditEventModel


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(self, actor_id: str, action: str, outcome: str, *, client_id: UUID | None = None, film_id: UUID | None = None, environment_id: UUID | None = None, metadata: dict | None = None) -> AuditEventModel:
        event = AuditEventModel(event_id=uuid4(), actor_id=actor_id, action=action, outcome=outcome, client_id=client_id, film_id=film_id, environment_id=environment_id, metadata=metadata or {})
        self.session.add(event)
        await self.session.flush()
        return event
