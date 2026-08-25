from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class SimilarityModel(Protocol):
    def similarity(self, reference: Any, candidate: Any) -> float: ...


@dataclass(frozen=True)
class ConsistencyResult:
    passed: bool
    score: float
    threshold: float


class CharacterConsistencyValidator:
    def __init__(self, model: SimilarityModel, threshold: float = 0.75) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.model = model
        self.threshold = threshold

    def validate(self, reference: Any, candidate: Any) -> ConsistencyResult:
        score = float(self.model.similarity(reference, candidate))
        if not 0.0 <= score <= 1.0:
            raise ValueError("similarity model must return a value between 0 and 1")
        return ConsistencyResult(score >= self.threshold, score, self.threshold)
