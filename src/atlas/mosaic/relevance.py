"""Lexical relevance score in the [0, 1] range."""
from __future__ import annotations
import re
from atlas.mosaic.intent import normalize

def relevance_score(query: str, content: str) -> float:
    q = set(re.findall(r"[a-z0-9]{3,}", normalize(query)))
    d = set(re.findall(r"[a-z0-9]{3,}", normalize(content)))
    if not q or not d:
        return 0.0
    return round(len(q & d) / len(q), 4)
