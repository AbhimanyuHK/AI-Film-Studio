from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestContext:
    subject: str
    client_id: str
    film_id: str
    roles: frozenset[str] = frozenset()


_current: ContextVar[RequestContext | None] = ContextVar("film_request_context", default=None)


def set_request_context(context: RequestContext) -> None:
    if not context.subject or not context.client_id or not context.film_id:
        raise ValueError("subject, client_id and film_id are required")
    _current.set(context)


def get_request_context() -> RequestContext:
    context = _current.get()
    if context is None:
        raise RuntimeError("request context is not initialized")
    return context


def clear_request_context() -> None:
    _current.set(None)
