from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class JobLease:
    job_id: str
    film_id: str
    stage: str
    attempts: int = 0


class GPUJobScheduler:
    """Small in-process scheduler contract; production deployment can replace it with a queue."""

    def __init__(self, concurrency: int = 1) -> None:
        if concurrency < 1:
            raise ValueError("concurrency must be positive")
        self._semaphore = asyncio.Semaphore(concurrency)

    async def run(self, lease: JobLease, worker, inputs: dict):
        async with self._semaphore:
            lease.attempts += 1
            return await worker.execute(
                job_id=lease.job_id,
                film_id=lease.film_id,
                stage=lease.stage,
                inputs=inputs,
            )
