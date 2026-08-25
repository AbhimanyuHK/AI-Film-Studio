from __future__ import annotations

from .access_control import FilmAccessController, Principal
from .job_contract import AIJob
from .request_context import RequestContext


class AIJobValidator:
    """Validates every queued AI job before execution."""

    def __init__(self, access: FilmAccessController) -> None:
        self.access = access

    def validate(self, principal: Principal, job: AIJob) -> RequestContext:
        self.access.authorize(principal, job.client_id, job.film_id)
        if job.attempt < 1:
            raise ValueError("job attempt must be >= 1")
        return RequestContext(
            subject=principal.subject,
            client_id=job.client_id,
            film_id=job.film_id,
            roles=principal.roles,
        )
