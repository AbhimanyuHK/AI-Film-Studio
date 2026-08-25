from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .access_control import FilmAccessController, Principal
from .job_contract import AIJob
from .job_state import JobState, JobStateMachine, JobStatus
from .job_validation import AIJobValidator


@dataclass(frozen=True)
class ExecutionResult:
    job_id: str
    state: JobState
    result: object | None = None


class AIJobExecutor:
    """Executes one validated job with explicit retry and terminal states."""

    def __init__(self, access: FilmAccessController, handlers: dict[str, Callable[[AIJob], object]], max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.validator = AIJobValidator(access)
        self.handlers = handlers
        self.max_attempts = max_attempts

    def execute(self, principal: Principal, job: AIJob) -> ExecutionResult:
        self.validator.validate(principal, job)
        machine = JobStateMachine(job.job_id)
        handler = self.handlers.get(job.operation.value)
        if handler is None:
            machine.transition(JobStatus.FAILED, f"no handler registered for {job.operation.value}")
            return ExecutionResult(job.job_id, machine.state)

        while True:
            machine.transition(JobStatus.RUNNING)
            try:
                result = handler(job)
                machine.transition(JobStatus.COMPLETED)
                return ExecutionResult(job.job_id, machine.state, result)
            except Exception as exc:
                if machine.state.attempt >= self.max_attempts:
                    machine.transition(JobStatus.FAILED, str(exc))
                    return ExecutionResult(job.job_id, machine.state)
                machine.transition(JobStatus.RETRYING, str(exc))
