from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, headers={"X-Actor-ID": "ci-test-suite"})


def create_film() -> str:
    client_response = client.post("/api/v1/clients", json={"name": "Environment Test Client"})
    assert client_response.status_code == 201
    response = client.post(
        "/api/v1/films",
        json={
            "client_id": client_response.json()["client_id"],
            "name": "Environment Film",
            "source_language": "kn",
            "target_languages": ["en-US"],
        },
    )
    assert response.status_code == 201
    return response.json()["film_id"]


def test_one_environment_per_film() -> None:
    film_id = create_film()
    payload = {
        "aws_account_id": "123456789012",
        "aws_region": "us-east-1",
        "subdomain": "film-a-test",
    }

    first = client.post(f"/api/v1/films/{film_id}/environment", json=payload)
    assert first.status_code == 201

    second = client.post(f"/api/v1/films/{film_id}/environment", json=payload)
    assert second.status_code == 409


def test_deployment_requires_environment() -> None:
    film_id = create_film()
    response = client.post(
        f"/api/v1/films/{film_id}/deployments",
        json={"version": "0.1.0"},
    )
    assert response.status_code == 404


def test_create_deployment() -> None:
    film_id = create_film()
    environment = client.post(
        f"/api/v1/films/{film_id}/environment",
        json={
            "aws_account_id": "123456789013",
            "aws_region": "us-east-1",
            "subdomain": "film-deploy-test",
        },
    )
    assert environment.status_code == 201

    deployment = client.post(
        f"/api/v1/films/{film_id}/deployments",
        json={"version": "0.1.0"},
    )
    assert deployment.status_code == 201
    assert deployment.json()["status"] == "queued"
