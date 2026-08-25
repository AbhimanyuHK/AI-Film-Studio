from collections.abc import Awaitable, Callable
from typing import Any


JobHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class JobWorker:
    """Provider-neutral worker boundary.

    The worker intentionally does not execute AI workloads yet. Concrete GPU
    workers will be plugged in behind this interface so the control plane is
    independent of the model/runtime provider.
    """

    def __init__(self) -> None:
        self.handlers: dict[str, JobHandler] = {}

    def register(self, job_type: str, handler: JobHandler) -> None:
        self.handlers[job_type] = handler

    async def execute(self, job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        handler = self.handlers.get(job_type)
        if handler is None:
            raise RuntimeError(f"No worker registered for job type: {job_type}")
        return await handler(payload)
