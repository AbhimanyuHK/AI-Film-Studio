from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class S3ArtifactRef:
    client_id: str
    film_id: str
    artifact_id: str
    kind: str
    bucket: str
    key: str
    sha256: str


class S3ArtifactStore:
    """Production artifact store using immutable client/film-scoped S3 keys."""

    def __init__(self, bucket: str, s3_client: Any, kms_key_id: str | None = None) -> None:
        if not bucket:
            raise ValueError("bucket is required")
        self.bucket = bucket
        self.s3 = s3_client
        self.kms_key_id = kms_key_id

    @staticmethod
    def _key(client_id: str, film_id: str, kind: str, artifact_id: str) -> str:
        if not all((client_id, film_id, kind, artifact_id)):
            raise ValueError("client_id, film_id, kind and artifact_id are required")
        return f"clients/{client_id}/films/{film_id}/{kind}/{artifact_id}"

    def put(self, client_id: str, film_id: str, artifact_id: str, kind: str, data: bytes, content_type: str | None = None) -> S3ArtifactRef:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        key = self._key(client_id, film_id, kind, artifact_id)
        digest = hashlib.sha256(data).hexdigest()
        extra: dict[str, Any] = {
            "Metadata": {"client-id": client_id, "film-id": film_id, "sha256": digest},
            "ServerSideEncryption": "aws:kms" if self.kms_key_id else "AES256",
        }
        if self.kms_key_id:
            extra["SSEKMSKeyId"] = self.kms_key_id
        if content_type:
            extra["ContentType"] = content_type
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)
        return S3ArtifactRef(client_id, film_id, artifact_id, kind, self.bucket, key, digest)

    def get(self, client_id: str, film_id: str, artifact_id: str, kind: str) -> bytes:
        key = self._key(client_id, film_id, kind, artifact_id)
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()
