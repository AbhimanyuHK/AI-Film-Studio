import asyncio
import json
import os
import socket
from datetime import datetime, timezone

import asyncpg
import httpx

DATABASE_URL = os.environ["DATABASE_URL"]
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://ai-engine:8080").rstrip("/")
FILM_RUNTIME_URL_TEMPLATE = os.getenv("FILM_RUNTIME_URL_TEMPLATE", "").strip().rstrip("/")
WORKER_ID = os.getenv("WORKER_ID", socket.gethostname())
POLL_SECONDS = float(os.getenv("WORKER_POLL_SECONDS", "2"))
LEASE_SECONDS = int(os.getenv("WORKER_LEASE_SECONDS", "300"))
RECOVERY_SECONDS = float(os.getenv("WORKER_RECOVERY_SECONDS", "30"))


async def recover_expired(pool) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT recover_expired_job_leases()")


async def claim(pool):
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """
                SELECT j.job_id, j.film_id, j.environment_id, j.job_type,
                       j.payload, j.attempts, j.max_attempts, f.client_id
                FROM jobs j
                JOIN films f ON f.film_id = j.film_id
                WHERE j.status IN ('queued', 'retrying')
                  AND j.scheduled_at <= now()
                  AND j.attempts < j.max_attempts
                  AND NOT EXISTS (
                      SELECT 1
                      FROM job_dependencies d
                      JOIN jobs dep ON dep.job_id = d.depends_on_job_id
                      WHERE d.job_id = j.job_id
                        AND dep.status <> 'completed'
                  )
                ORDER BY j.scheduled_at, j.created_at
                FOR UPDATE OF j SKIP LOCKED
                LIMIT 1
                """
            )
            if not row:
                return None
            await conn.execute(
                """
                UPDATE jobs
                SET status='running', worker_id=$1,
                    lease_until=now() + ($2 * interval '1 second'),
                    started_at=now(), updated_at=now(), attempts=attempts+1
                WHERE job_id=$3
                """,
                WORKER_ID,
                LEASE_SECONDS,
                row["job_id"],
            )
            return dict(row)


async def finish(pool, job_id, *, result=None, error=None, retry=False):
    async with pool.acquire() as conn:
        if retry:
            await conn.execute(
                """
                UPDATE jobs
                SET status='retrying', retry_count=retry_count+1,
                    worker_id=NULL, lease_until=NULL, error_code=$2, updated_at=now()
                WHERE job_id=$1 AND worker_id=$3
                """,
                job_id,
                error,
                WORKER_ID,
            )
        elif error:
            await conn.execute(
                """
                UPDATE jobs
                SET status='failed', worker_id=NULL, lease_until=NULL,
                    error_code=$2, result=$3::jsonb, completed_at=now(), updated_at=now()
                WHERE job_id=$1 AND worker_id=$4
                """,
                job_id,
                error,
                json.dumps(result or {}),
                WORKER_ID,
            )
        else:
            await conn.execute(
                """
                UPDATE jobs
                SET status='completed', worker_id=NULL, lease_until=NULL,
                    result=$2::jsonb, completed_at=now(), updated_at=now()
                WHERE job_id=$1 AND worker_id=$3
                """,
                job_id,
                json.dumps(result or {}),
                WORKER_ID,
            )


def runtime_url(job: dict) -> str | None:
    if not FILM_RUNTIME_URL_TEMPLATE:
        return None
    return FILM_RUNTIME_URL_TEMPLATE.format(
        film_id=job["film_id"], environment_id=job["environment_id"]
    )


async def execute(pool, job):
    payload = job["payload"] or {}
    body = {
        "job_id": str(job["job_id"]),
        "client_id": str(job["client_id"]),
        "film_id": str(job["film_id"]),
        "environment_id": str(job["environment_id"]),
        "operation": job["job_type"],
        "payload": payload,
    }
    try:
        target = runtime_url(job)
        if target:
            url = f"{target}/v1/jobs/execute"
        else:
            url = f"{AI_ENGINE_URL}/v1/jobs/execute"
        async with httpx.AsyncClient(timeout=1800) as client:
            response = await client.post(url, json=body)
            response.raise_for_status()
            data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("execution service returned a non-object response")
        await finish(pool, job["job_id"], result=data)
    except Exception as exc:
        retry = job["attempts"] < job["max_attempts"]
        await finish(pool, job["job_id"], error=type(exc).__name__, retry=retry)


async def main_loop():
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    last_recovery = 0.0
    try:
        while True:
            now = datetime.now(timezone.utc).timestamp()
            if now - last_recovery >= RECOVERY_SECONDS:
                try:
                    await recover_expired(pool)
                finally:
                    last_recovery = now
            job = await claim(pool)
            if job:
                await execute(pool, job)
            else:
                await asyncio.sleep(POLL_SECONDS)
    finally:
        await pool.close()


def main():
    asyncio.run(main_loop())


if __name__ == "__main__":
    main()
