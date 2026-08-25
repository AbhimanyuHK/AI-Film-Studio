from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .consistency import CharacterConsistencyValidator
from .retry_policy import RetryPolicy, RetryResult, generate_until_consistent


@dataclass(frozen=True)
class ConsistentGenerationResult:
    output: Any
    attempts: int
    score: float


class ConsistentImageGenerator:
    """Generate, validate identity, and retry within a bounded GPU budget."""

    def __init__(self, validator: CharacterConsistencyValidator, policy: RetryPolicy | None = None) -> None:
        self.validator = validator
        self.policy = policy or RetryPolicy()

    def generate(self, reference: Any, generate: Callable[[int], Any]) -> ConsistentGenerationResult:
        def score(candidate: Any) -> float:
            return self.validator.validate(reference, candidate).score

        result: RetryResult[Any] = generate_until_consistent(generate, score, self.policy)
        return ConsistentGenerationResult(result.value, result.attempts, result.score)
