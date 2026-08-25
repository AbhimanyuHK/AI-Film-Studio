from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel


class AuditEvent(BaseModel):
    actor_id: str
    action: str
    outcome: str
    client_id: UUID | None = None
    film_id: UUID | None = None
    environment_id: UUID | None = None
    metadata: dict = {}
    created_at: datetime


def build_audit_event(
    *,
    actor_id: str,
    action: str,
    outcome: str,
    client_id: UUID | None = None,
    film_id: UUID | None = None,
    environment_id: UUID | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    return AuditEvent(
        actor_id=actor_id,
        action=action,
        outcome=outcome,
        client_id=client_id,
        film_id=film_id,
        environment_id=environment_id,
        metadata=metadata or {},
        created_at=datetime.now(timezone.utc),
    )
