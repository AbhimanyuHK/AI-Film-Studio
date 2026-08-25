from dataclasses import dataclass
import os


@dataclass(frozen=True)
class WorkerConfig:
    worker_id: str
    device: str
    max_concurrency: int
    s3_bucket: str


def load_worker_config() -> WorkerConfig:
    concurrency = int(os.getenv("GPU_WORKER_CONCURRENCY", "1"))
    if concurrency < 1:
        raise ValueError("GPU_WORKER_CONCURRENCY must be positive")
    bucket = os.getenv("FILM_ASSET_BUCKET")
    if not bucket:
        raise RuntimeError("FILM_ASSET_BUCKET is required for a GPU worker")
    return WorkerConfig(
        worker_id=os.getenv("GPU_WORKER_ID", "gpu-worker-1"),
        device=os.getenv("GPU_DEVICE", "cuda"),
        max_concurrency=concurrency,
        s3_bucket=bucket,
    )
