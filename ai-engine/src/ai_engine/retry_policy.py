from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    threshold: float = 0.75

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")


@dataclass(frozen=True)
class RetryResult(Generic[T]):
    value: T
    attempts: int
    score: float


def generate_until_consistent(
    generate: Callable[[int], T],
    score: Callable[[T], float],
    policy: RetryPolicy = RetryPolicy(),
) -> RetryResult[T]:
    """Retry generation with deterministic attempt seeds until consistency passes."""
    last_value: T | None = None
    last_score = 0.0
    for attempt in range(policy.max_attempts):
        value = generate(attempt)
        last_value = value
        last_score = float(score(value))
        if not 0.0 <= last_score <= 1.0:
            raise ValueError("score must be between 0 and 1")
        if last_score >= policy.threshold:
            return RetryResult(value, attempt + 1, last_score)
    assert last_value is not None
    raise RuntimeError(
        f"character consistency failed after {policy.max_attempts} attempts; "
        f"last score={last_score:.3f}, threshold={policy.threshold:.3f}"
    )
