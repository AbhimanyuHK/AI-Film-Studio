"""End-to-end local/staging smoke test for the control-plane job path.

Usage:
    python deployment/smoke_test.py

Requires a running stack and APP_BASE_URL, defaulting to http://localhost:8000.
The test uses development X-Actor-Id authentication and a deterministic AI
integration executor; it does not claim that media was generated.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000").rstrip("/")
ACTOR = os.getenv("SMOKE_ACTOR_ID", "smoke-test")


def request(method: str, path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "X-Actor-Id": ACTOR},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {detail}") from exc


def main() -> int:
    request("GET", "/health")

    client = request("POST", "/api/v1/clients", {"name": f"Smoke Client {uuid.uuid4().hex[:8]}"})
    client_id = client["client_id"]

    film = request(
        "POST",
        "/api/v1/films",
        {
            "client_id": client_id,
            "name": f"Smoke Film {uuid.uuid4().hex[:8]}",
            "source_language": "en",
            "target_languages": ["en"],
        },
    )
    film_id = film["film_id"]

    environment = request(
        "POST",
        f"/api/v1/films/{film_id}/environment",
        {
            "aws_account_id": "123456789012",
            "aws_region": "us-east-1",
            "subdomain": f"smoke-{uuid.uuid4().hex[:10]}",
        },
    )

    job = request(
        "POST",
        f"/api/v1/films/{film_id}/jobs",
        {
            "job_type": "script_analysis",
            "idempotency_key": f"smoke-{uuid.uuid4()}",
            "payload": {"script": "A short scene for integration testing."},
        },
    )
    job_id = job["job_id"]

    deadline = time.time() + 90
    while time.time() < deadline:
        current = request("GET", f"/api/v1/jobs/{job_id}")
        if current["status"] == "completed":
            print(json.dumps({"status": "passed", "client_id": client_id, "film_id": film_id, "environment_id": environment["environment_id"], "job_id": job_id}, indent=2))
            return 0
        if current["status"] == "failed":
            print(json.dumps(current, indent=2), file=sys.stderr)
            return 1
        time.sleep(2)

    print(f"Timed out waiting for job {job_id}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
