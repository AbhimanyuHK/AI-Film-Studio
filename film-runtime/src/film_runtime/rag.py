from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    text: str
    source: str
    score: float = 0.0


class FilmKnowledgeIndex:
    """Film-scoped retrieval boundary.

    The runtime owns the index. A production deployment can replace this
    implementation with pgvector/OpenSearch while keeping the same interface.
    """

    def __init__(self) -> None:
        self._chunks: list[KnowledgeChunk] = []

    def upsert(self, chunk: KnowledgeChunk) -> None:
        self._chunks = [c for c in self._chunks if c.chunk_id != chunk.chunk_id]
        self._chunks.append(chunk)

    def search(self, query: str, limit: int = 8) -> list[KnowledgeChunk]:
        terms = {t.lower() for t in query.split() if t.strip()}
        if not terms:
            return []
        ranked = []
        for chunk in self._chunks:
            words = set(chunk.text.lower().split())
            score = len(terms & words) / max(len(terms), 1)
            if score:
                ranked.append(KnowledgeChunk(chunk.chunk_id, chunk.text, chunk.source, score))
        return sorted(ranked, key=lambda x: x.score, reverse=True)[:limit]
