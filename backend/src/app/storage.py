from __future__ import annotations

import os
from uuid import UUID

import boto3


class FilmStorage:
    """S3 storage boundary. Bucket is environment-specific; object keys are film-scoped."""

    def __init__(self, bucket: str | None = None, region: str | None = None) -> None:
        self.bucket = bucket or os.environ["FILM_ASSET_BUCKET"]
        self.client = boto3.client("s3", region_name=region or os.getenv("AWS_REGION"))

    @staticmethod
    def object_key(film_id: UUID, asset_type: str, filename: str) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        return f"films/{film_id}/{asset_type}/{safe_name}"

    def presigned_upload(self, key: str, content_type: str, expires: int = 900) -> str:
        return self.client.generate_presigned_url(
            "put_object", Params={"Bucket": self.bucket, "Key": key, "ContentType": content_type}, ExpiresIn=expires
        )

    def presigned_download(self, key: str, expires: int = 900) -> str:
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=expires
        )
