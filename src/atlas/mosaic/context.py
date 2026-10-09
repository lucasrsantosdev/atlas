"""Context filtering; deliberately does not persist memories."""
from __future__ import annotations
from collections.abc import Iterable
from atlas.mosaic.models import ContextItem
from atlas.mosaic.relevance import relevance_score

def select_context(query: str, available: Iterable[ContextItem], *, limit: int = 5, min_score: float = 0.1) -> tuple[ContextItem, ...]:
    if limit <= 0:
        return ()
    ranked: list[tuple[float, int, ContextItem]] = []
    for i, item in enumerate(available):
        score = max(relevance_score(query, item.content), min(max(item.relevance, 0.0), 1.0))
        if score >= min_score:
            ranked.append((score, i, ContextItem(content=item.content, source=item.source, relevance=score, metadata=dict(item.metadata))))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return tuple(item for _, _, item in ranked[:limit])
