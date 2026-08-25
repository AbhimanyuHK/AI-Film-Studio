from uuid import UUID

from app.storage import FilmStorage


class StorageService:
    def __init__(self, storage: FilmStorage | None = None) -> None:
        self.storage = storage or FilmStorage()

    def create_upload(self, film_id: UUID, asset_type: str, filename: str, content_type: str) -> tuple[str, str]:
        key = self.storage.object_key(film_id, asset_type, filename)
        return key, self.storage.presigned_upload(key, content_type)

    def create_download(self, object_key: str) -> str:
        return self.storage.presigned_download(object_key)
