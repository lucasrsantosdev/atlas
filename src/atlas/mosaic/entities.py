"""Small explainable entity extractor; no external network calls."""
from __future__ import annotations
import re

def extract_entities(text: str) -> tuple[str, ...]:
    if not text.strip():
        return ()
    patterns = [
        r"\bATLAS(?:\.IA)?\b", r"\bMosaic\b", r"\bPython\b",
        r"\bOllama\b", r"\bQwen(?:2\.5)?\b", r"\bESP32\b",
        r"\bArduino\b", r"\bGitHub\b", r"\bSQLite\b",
        r"\bRAG\b", r"\bAtlas Mini\b",
        r"\b[A-Za-z0-9_.-]+\.(?:py|md|txt|json|yaml|yml|pdf)\b",
    ]
    found: list[tuple[int,str]] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            found.append((match.start(), match.group(0)))
    seen: set[str] = set()
    result: list[str] = []
    for _, value in sorted(found, key=lambda x: x[0]):
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return tuple(result)
