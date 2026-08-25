from fastapi import Header, HTTPException

from .config import settings


def enforce_scope(
    client_id: str | None = Header(default=None, alias='X-Client-Id'),
    film_id: str | None = Header(default=None, alias='X-Film-Id'),
    environment_id: str | None = Header(default=None, alias='X-Environment-Id'),
) -> None:
    """Hard boundary: this process can serve exactly one film environment."""
    if client_id != settings.runtime_client_id:
        raise HTTPException(status_code=403, detail='Client scope denied')
    if film_id != settings.runtime_film_id:
        raise HTTPException(status_code=403, detail='Film scope denied')
    if environment_id != settings.runtime_environment_id:
        raise HTTPException(status_code=403, detail='Environment scope denied')


def validate_payload_scope(payload: dict) -> None:
    for key, expected in (
        ('client_id', settings.runtime_client_id),
        ('film_id', settings.runtime_film_id),
        ('environment_id', settings.runtime_environment_id),
    ):
        if key in payload and str(payload[key]) != expected:
            raise HTTPException(status_code=403, detail=f'{key} scope denied')
