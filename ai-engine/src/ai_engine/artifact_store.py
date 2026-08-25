from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ArtifactRef:
    client_id: str
    film_id: str
    artifact_id: str
    kind: str
    path: str
    sha256: str


class LocalArtifactStore:
    """Development store with mandatory client/film-scoped artifact paths."""

    def __init__(self, root: str = "artifacts") -> None:
        self.root = Path(root).resolve()

    def _target(self, client_id: str, film_id: str, artifact_id: str, kind: str) -> Path:
        if not client_id or not film_id or not artifact_id or not kind:
            raise ValueError("client_id, film_id, artifact_id and kind are required")
        return self.root / "clients" / client_id / "films" / film_id / kind / artifact_id

    def save_bytes(self, client_id: str, film_id: str, artifact_id: str, kind: str, data: bytes) -> ArtifactRef:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        target = self._target(client_id, film_id, artifact_id, kind)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        return ArtifactRef(client_id, film_id, artifact_id, kind, str(target), digest)

    def save_image(self, client_id: str, film_id: str, shot_id: str, image: Any) -> ArtifactRef:
        from io import BytesIO
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return self.save_bytes(client_id, film_id, shot_id, "shots", buffer.getvalue())

    def get_bytes(self, client_id: str, film_id: str, artifact_id: str, kind: str) -> bytes:
        target = self._target(client_id, film_id, artifact_id, kind)
        if not target.is_file():
            raise FileNotFoundError("artifact not found in requested film scope")
        return target.read_bytes()
