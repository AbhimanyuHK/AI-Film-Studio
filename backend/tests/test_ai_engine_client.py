import asyncio
from uuid import uuid4

import pytest

from app.ai_engine_client import AIEngineClient, AIEngineError


def test_ai_engine_client_rejects_non_json_response(monkeypatch):
    class Response:
        status_code = 200

        def json(self):
            return ["invalid"]

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, *args, **kwargs):
            return Response()

    monkeypatch.setattr("app.ai_engine_client.httpx.AsyncClient", lambda **kwargs: Client())
    client = AIEngineClient("http://test")

    async def run():
        with pytest.raises(AIEngineError):
            await client.execute_job(job_id=uuid4(), client_id=uuid4(), film_id=uuid4(), operation="video_generation", payload={}, environment_id=uuid4())

    asyncio.run(run())
