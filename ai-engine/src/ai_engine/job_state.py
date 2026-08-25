from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


_TERMINAL = {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}


@dataclass(frozen=True)
class JobState:
    job_id: str
    status: JobStatus
    attempt: int
    updated_at: datetime
    error: str | None = None


class JobStateMachine:
    """Deterministic state machine for a DB-backed job repository."""

    def __init__(self, job_id: str) -> None:
        if not job_id:
            raise ValueError("job_id is required")
        self.state = JobState(job_id, JobStatus.QUEUED, 1, datetime.now(timezone.utc))

    def transition(self, status: JobStatus, error: str | None = None) -> JobState:
        current = self.state.status
        allowed = {
            JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.CANCELLED},
            JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.RETRYING, JobStatus.FAILED, JobStatus.CANCELLED},
            JobStatus.RETRYING: {JobStatus.RUNNING, JobStatus.CANCELLED},
        }
        if current in _TERMINAL:
            raise RuntimeError(f"job is already terminal: {current.value}")
        if status not in allowed.get(current, set()):
            raise ValueError(f"invalid transition: {current.value} -> {status.value}")
        attempt = self.state.attempt + 1 if status == JobStatus.RETRYING else self.state.attempt
        self.state = JobState(self.state.job_id, status, attempt, datetime.now(timezone.utc), error)
        return self.state
