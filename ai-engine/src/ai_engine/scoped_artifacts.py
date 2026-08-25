from __future__ import annotations

from typing import Protocol

from .access_control import FilmAccessController, Principal
from .artifact_store import ArtifactRef, LocalArtifactStore


class ScopedArtifactRepository(Protocol):
    def save_bytes(self, client_id: str, film_id: str, artifact_id: str, kind: str, data: bytes) -> ArtifactRef: ...
    def get_bytes(self, client_id: str, film_id: str, artifact_id: str, kind: str) -> bytes: ...


class AuthorizedArtifactStore:
    """Authorization wrapper: storage is never accessed before scope validation."""

    def __init__(self, store: ScopedArtifactRepository, access: FilmAccessController) -> None:
        self.store = store
        self.access = access

    def save_bytes(self, principal: Principal, client_id: str, film_id: str, artifact_id: str, kind: str, data: bytes) -> ArtifactRef:
        self.access.authorize_artifact(principal, client_id, film_id)
        return self.store.save_bytes(client_id, film_id, artifact_id, kind, data)

    def get_bytes(self, principal: Principal, client_id: str, film_id: str, artifact_id: str, kind: str) -> bytes:
        self.access.authorize_artifact(principal, client_id, film_id)
        return self.store.get_bytes(client_id, film_id, artifact_id, kind)
