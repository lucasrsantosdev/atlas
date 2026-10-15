"""Bounded deterministic lexical retrieval for RAGNES.

Search results are evidence with source paths and line ranges, never instructions
or tool authorization. No database, index, or external dependency is required.
"""
import re
from pathlib import Path
from typing import Any

from app.context.artifacts import (
    MAX_ARTIFACT_BYTES,
    _resolve_workspace_file,
    _workspace_root,
    list_workspace_artifacts,
)

MAX_SEARCH_RESULTS = 10
MAX_FILES_SCANNED = 100
MAX_SEARCH_BYTES = 5_000_000
MAX_SNIPPET_CHARS = 700
MAX_MATCHES_PER_FILE = 3
MIN_TERM_LENGTH = 2

_STOP_WORDS = {
    "a", "as", "o", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "sem", "e", "ou", "que", "como", "qual", "quais", "onde", "quando",
    "me", "te", "se", "ao", "aos", "é", "ser", "foi", "são", "the", "and",
    "for", "from", "with", "this", "that", "what", "where", "how", "are",
}


def _terms(query: str) -> list[str]:
    terms = [
        token.casefold()
        for token in re.findall(r"[\w.-]+", query, flags=re.UNICODE)
        if len(token) >= MIN_TERM_LENGTH and token.casefold() not in _STOP_WORDS
    ]
    return list(dict.fromkeys(terms))[:12]


def search_workspace_artifacts(
    workspace: str | Path,
    query: str,
    *,
    max_results: int = MAX_SEARCH_RESULTS,
    max_files_scanned: int = MAX_FILES_SCANNED,
    max_total_bytes: int = MAX_SEARCH_BYTES,
) -> dict[str, Any]:
    """Search filenames and UTF-8 text within strict workspace and work limits."""
    if not 1 <= max_results <= MAX_SEARCH_RESULTS:
        raise ValueError(f"max_results must be between 1 and {MAX_SEARCH_RESULTS}")
    if not 1 <= max_files_scanned <= MAX_FILES_SCANNED:
        raise ValueError(f"max_files_scanned must be between 1 and {MAX_FILES_SCANNED}")
    if not 1 <= max_total_bytes <= MAX_SEARCH_BYTES:
        raise ValueError(f"max_total_bytes must be between 1 and {MAX_SEARCH_BYTES}")

    terms = _terms(query)
    if not terms:
        return {"query": query, "terms": [], "results": [], "scanned_files": 0, "truncated": False}

    root = _workspace_root(workspace)
    inventory = list_workspace_artifacts(root)
    ranked: list[dict[str, Any]] = []
    scanned_files = 0
    bytes_scanned = 0
    truncated = inventory["truncated"]

    for entry in inventory["entries"]:
        if scanned_files >= max_files_scanned or bytes_scanned >= max_total_bytes:
            truncated = True
            break
        path_text = entry["path"]
        # Project instruction files are loaded separately by Context Manager.
        if Path(path_text).name.casefold() in {"agents.md", "agent.md"}:
            continue
        size = entry["size_bytes"]
        if size > MAX_ARTIFACT_BYTES or size > max_total_bytes - bytes_scanned:
            truncated = True
            continue
        try:
            path = _resolve_workspace_file(root, path_text)
            content = path.read_text(encoding="utf-8")
        except (OSError, RuntimeError, ValueError, UnicodeError):
            continue

        scanned_files += 1
        bytes_scanned += size
        folded_path = path_text.casefold()
        folded_name = path.name.casefold()
        score = 0
        matched: set[str] = set()
        for term in terms:
            if term in folded_path:
                score += 8
                matched.add(term)
            elif term in folded_name:
                score += 5
                matched.add(term)

        lines = content.splitlines()
        matching_lines: list[tuple[int, int, set[str]]] = []
        for line_number, line in enumerate(lines, start=1):
            folded_line = line.casefold()
            line_terms = {term for term in terms if term in folded_line}
            if line_terms:
                line_score = 2 * len(line_terms)
                score += line_score
                matched.update(line_terms)
                matching_lines.append((line_number, line_score, line_terms))

        if not matched:
            continue
        if query.strip().casefold() in folded_path:
            score += 12
        elif query.strip().casefold() in content.casefold():
            score += 6

        snippets = []
        seen_lines: set[int] = set()
        for line_number, _, _ in sorted(matching_lines, key=lambda item: (-item[1], item[0])):
            if line_number in seen_lines:
                continue
            seen_lines.add(line_number)
            start = max(1, line_number - 1)
            end = min(len(lines), line_number + 1)
            snippet = "\n".join(lines[start - 1:end])
            if len(snippet) > MAX_SNIPPET_CHARS:
                snippet = snippet[:MAX_SNIPPET_CHARS] + " [trecho truncado]"
            snippets.append({
                "start_line": start,
                "end_line": end,
                "matched_line": line_number,
                "content": snippet,
            })
            if len(snippets) >= MAX_MATCHES_PER_FILE:
                break

        ranked.append({
            "path": path_text,
            "score": score,
            "matched_terms": sorted(matched),
            "size_bytes": size,
            "snippets": snippets,
        })

    ranked.sort(key=lambda item: (-item["score"], item["path"].casefold()))
    results = ranked[:max_results]
    if len(ranked) > max_results:
        truncated = True
    return {
        "query": query,
        "terms": terms,
        "results": results,
        "scanned_files": scanned_files,
        "bytes_scanned": bytes_scanned,
        "truncated": truncated,
    }
