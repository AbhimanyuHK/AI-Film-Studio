from __future__ import annotations

import io

import boto3

from .config import settings


class FilmObjectStore:
    def __init__(self) -> None:
        self.bucket = settings.s3_bucket
        self.prefix = settings.s3_prefix.strip('/')
        self.client = boto3.client('s3', region_name=settings.aws_region)

    def key(self, asset_id: str, filename: str) -> str:
        safe = filename.replace('..', '').lstrip('/')
        prefix = f'{self.prefix}/' if self.prefix else ''
        return f'{prefix}assets/{asset_id}/{safe}'

    def put_bytes(self, asset_id: str, filename: str, data: bytes, content_type: str = 'application/octet-stream') -> str:
        if not self.bucket:
            raise RuntimeError('S3_BUCKET is not configured')
        key = self.key(asset_id, filename)
        self.client.upload_fileobj(io.BytesIO(data), self.bucket, key, ExtraArgs={'ContentType': content_type})
        return key

    def presigned_get(self, key: str, expires: int = 900) -> str:
        if not self.bucket:
            raise RuntimeError('S3_BUCKET is not configured')
        return self.client.generate_presigned_url('get_object', Params={'Bucket': self.bucket, 'Key': key}, ExpiresIn=expires)
