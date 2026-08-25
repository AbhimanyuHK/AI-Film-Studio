from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ImageArtifact:
    film_id: str
    shot_id: str
    path: str
    sha256: str
    content_type: str = "image/png"


class LocalArtifactStore:
    """Development artifact store with the same film-scoped key contract used by S3."""

    def __init__(self, root: str = "artifacts") -> None:
        self.root = Path(root)

    def save_image(self, film_id: str, shot_id: str, image: Any) -> ImageArtifact:
        if not film_id or not shot_id:
            raise ValueError("film_id and shot_id are required")
        target = self.root / film_id / "shots" / f"{shot_id}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, format="PNG")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return ImageArtifact(film_id=film_id, shot_id=shot_id, path=str(target), sha256=digest)
