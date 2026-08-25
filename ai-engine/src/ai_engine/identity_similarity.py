from __future__ import annotations

from typing import Any


class CosineIdentitySimilarity:
    """Optional image-embedding similarity backend with an injected embedder."""

    def __init__(self, embedder: Any) -> None:
        self.embedder = embedder

    def similarity(self, reference: Any, candidate: Any) -> float:
        ref = self.embedder(reference)
        cand = self.embedder(candidate)
        dot = float((ref * cand).sum())
        ref_norm = float((ref * ref).sum()) ** 0.5
        cand_norm = float((cand * cand).sum()) ** 0.5
        if ref_norm == 0.0 or cand_norm == 0.0:
            return 0.0
        cosine = dot / (ref_norm * cand_norm)
        return max(0.0, min(1.0, (cosine + 1.0) / 2.0))
