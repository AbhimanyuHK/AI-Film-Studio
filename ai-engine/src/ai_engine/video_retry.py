from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class VideoRetryPolicy:
    max_attempts: int = 2
    threshold: float = 0.70

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")


@dataclass(frozen=True)
class VideoRetryResult:
    output: Any
    attempts: int
    score: float


def generate_valid_video(
    generate: Callable[[int], Any],
    score: Callable[[Any], float],
    policy: VideoRetryPolicy = VideoRetryPolicy(),
) -> VideoRetryResult:
    last_output: Any = None
    last_score = 0.0
    for attempt in range(policy.max_attempts):
        output = generate(attempt)
        last_output = output
        last_score = float(score(output))
        if not 0.0 <= last_score <= 1.0:
            raise ValueError("video score must be between 0 and 1")
        if last_score >= policy.threshold:
            return VideoRetryResult(output, attempt + 1, last_score)
    raise RuntimeError(
        f"video validation failed after {policy.max_attempts} attempts; "
        f"last score={last_score:.3f}, threshold={policy.threshold:.3f}"
    )
