import asyncio
import os
import socket
import uuid
from datetime import datetime, timezone

import asyncpg
import httpx

DATABASE_URL = os.environ["DATABASE_URL"]
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://ai-engine:8080")
WORKER_ID = os.getenv("WORKER_ID", socket.gethostname())
POLL_SECONDS = float(os.getenv("WORKER_POLL_SECONDS", "2"))
LEASE_SECONDS = int(os.getenv("WORKER_LEASE_SECONDS", "300"))

async def claim(pool):
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow("""
                SELECT job_id, film_id, environment_id, job_type, payload, attempts, max_attempts
                FROM jobs
                WHERE status IN ('queued','retrying')
                  AND scheduled_at <= now()
                  AND (lease_until IS NULL OR lease_until < now())
                ORDER BY scheduled_at, created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            """)
            if not row:
                return None
            await conn.execute("""
                UPDATE jobs SET status='running', worker_id=$1,
                    lease_until=now() + ($2 * interval '1 second'),
                    attempts=attempts+1, updated_at=now()
                WHERE job_id=$3
            """, WORKER_ID, LEASE_SECONDS, row["job_id"])
            return dict(row)

async def finish(pool, job_id, result=None, error=None, retry=False):
    async with pool.acquire() as conn:
        if retry:
            await conn.execute("""
                UPDATE jobs SET status='retrying', retry_count=retry_count+1,
                    worker_id=NULL, lease_until=NULL, error_code=$2, updated_at=now()
                WHERE job_id=$1
            """, job_id, error)
        elif error:
            await conn.execute("""
                UPDATE jobs SET status='failed', worker_id=NULL, lease_until=NULL,
                    error_code=$2, result=$3::jsonb, completed_at=now(), updated_at=now()
                WHERE job_id=$1
            """, job_id, error, result or '{}')
        else:
            await conn.execute("""
                UPDATE jobs SET status='completed', worker_id=NULL, lease_until=NULL,
                    result=$2::jsonb, completed_at=now(), updated_at=now()
                WHERE job_id=$1
            """, job_id, result or '{}')

async def execute(pool, job):
    payload = job["payload"] or {}
    body = {"job_id": str(job["job_id"]), "film_id": str(job["film_id"]),
            "environment_id": str(job["environment_id"]), "job_type": job["job_type"], "payload": payload}
    try:
        async with httpx.AsyncClient(timeout=1800) as client:
            response = await client.post(f"{AI_ENGINE_URL}/v1/jobs/execute", json=body)
            response.raise_for_status()
            await finish(pool, job["job_id"], response.text)
    except Exception as exc:
        retry = job["attempts"] < job["max_attempts"]
        await finish(pool, job["job_id"], error=type(exc).__name__, retry=retry)

async def main_loop():
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    try:
        while True:
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
