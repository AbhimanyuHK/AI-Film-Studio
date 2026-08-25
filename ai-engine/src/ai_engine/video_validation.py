from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class VideoQualityScorer(Protocol):
    def score(self, video: Any) -> float: ...


@dataclass(frozen=True)
class VideoValidation:
    passed: bool
    score: float
    threshold: float


class VideoValidator:
    def __init__(self, scorer: VideoQualityScorer, threshold: float = 0.70) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.scorer = scorer
        self.threshold = threshold

    def validate(self, video: Any) -> VideoValidation:
        score = float(self.scorer.score(video))
        if not 0.0 <= score <= 1.0:
            raise ValueError("video scorer must return a value between 0 and 1")
        return VideoValidation(score >= self.threshold, score, self.threshold)
