from fastapi.testclient import TestClient

from ai_engine.http_api import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_execute_requires_scope() -> None:
    response = TestClient(app).post("/v1/jobs/execute", json={"operation": "video_generation"})
    assert response.status_code == 422
