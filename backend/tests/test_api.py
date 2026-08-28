from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, headers={"X-Actor-ID": "ci-test-suite"})


def test_create_client_and_film() -> None:
    client_response = client.post("/api/v1/clients", json={"name": "Client One"})
    assert client_response.status_code == 201
    client_id = client_response.json()["client_id"]

    film_response = client.post(
        "/api/v1/films",
        json={
            "client_id": client_id,
            "name": "Film A",
            "source_language": "kn",
            "target_languages": ["hi", "en-US"],
        },
    )
    assert film_response.status_code == 201
    assert film_response.json()["client_id"] == client_id


def test_film_requires_existing_client() -> None:
    response = client.post(
        "/api/v1/films",
        json={
            "client_id": "00000000-0000-0000-0000-000000000000",
            "name": "Film A",
            "source_language": "kn",
            "target_languages": [],
        },
    )
    assert response.status_code == 404
