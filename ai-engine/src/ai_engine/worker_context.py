from __future__ import annotations

from dataclasses import dataclass

from .access_control import FilmAccessController, Principal
from .request_context import RequestContext


@dataclass(frozen=True)
class WorkerJob:
    job_id: str
    client_id: str
    film_id: str
    operation: str


class WorkerContextValidator:
    """Reject jobs whose tenant/film scope does not match the worker identity."""

    def __init__(self, access: FilmAccessController) -> None:
        self.access = access

    def validate(self, principal: Principal, job: WorkerJob) -> RequestContext:
        self.access.authorize(principal, job.client_id, job.film_id)
        if not job.job_id or not job.operation:
            raise ValueError("job_id and operation are required")
        return RequestContext(subject=principal.subject, client_id=job.client_id, film_id=job.film_id, roles=principal.roles)
