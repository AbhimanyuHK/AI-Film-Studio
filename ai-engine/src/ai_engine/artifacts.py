from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import BinaryIO


@dataclass(frozen=True)
class Artifact:
    film_id: str
    object_key: str
    content_type: str
    size_bytes: int
    checksum: str


def describe_file(film_id: str, object_key: str, content_type: str, file: BinaryIO) -> Artifact:
    digest = sha256()
    size = 0
    while chunk := file.read(1024 * 1024):
        digest.update(chunk)
        size += len(chunk)
    return Artifact(film_id, object_key, content_type, size, digest.hexdigest())
