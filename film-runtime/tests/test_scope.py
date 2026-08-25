import os

os.environ.setdefault('RUNTIME_CLIENT_ID', 'client-1')
os.environ.setdefault('RUNTIME_FILM_ID', 'film-1')
os.environ.setdefault('RUNTIME_ENVIRONMENT_ID', 'env-1')

from film_runtime.config import settings
from film_runtime.scope import validate_payload_scope


def test_scope_accepts_runtime_film():
    validate_payload_scope({'client_id': settings.runtime_client_id, 'film_id': settings.runtime_film_id, 'environment_id': settings.runtime_environment_id})


def test_scope_rejects_other_film():
    try:
        validate_payload_scope({'film_id': 'other-film'})
    except Exception as exc:
        assert getattr(exc, 'status_code', None) == 403
    else:
        raise AssertionError('cross-film payload was accepted')
