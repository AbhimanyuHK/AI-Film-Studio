from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Principal:
    subject: str
    client_id: str
    film_ids: frozenset[str] = frozenset()
    roles: frozenset[str] = frozenset()


class FilmAccessController:
    """Application-layer authorization for client and film-scoped resources."""

    def __init__(self, admin_roles: Iterable[str] = ("platform-admin",)) -> None:
        self.admin_roles = frozenset(admin_roles)

    def authorize(self, principal: Principal, client_id: str, film_id: str) -> None:
        if principal.client_id != client_id:
            raise PermissionError("principal is not authorized for this client")
        if principal.roles & self.admin_roles:
            return
        if film_id not in principal.film_ids:
            raise PermissionError("principal is not authorized for this film")

    def authorize_artifact(self, principal: Principal, client_id: str, film_id: str) -> None:
        self.authorize(principal, client_id, film_id)
