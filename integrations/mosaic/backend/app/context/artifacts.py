"""Safe, bounded artifact discovery and direct reads for RAGNES.

This module returns workspace-relative provenance and never follows symlinks.
It does not modify files or grant any tool permissions.
"""
from pathlib import Path
from typing import Any

MAX_INVENTORY_ENTRIES = 200
MAX_INVENTORY_DEPTH = 3
MAX_ARTIFACT_BYTES = 1_000_000
MAX_EXCERPT_LINES = 200
MAX_EXCERPT_CHARS = 20_000
SKIPPED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mosaic",
}


def _workspace_root(workspace: str | Path) -> Path:
    try:
        root = Path(workspace).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("The active workspace does not exist") from exc
    if not root.is_dir():
        raise ValueError("The active workspace must be a directory")
    return root


def _resolve_workspace_file(root: Path, relative_path: str) -> Path:
    if not relative_path or "\x00" in relative_path:
        raise ValueError("A non-empty workspace-relative path is required")
    supplied = Path(relative_path)
    if supplied.is_absolute() or any(part == ".." for part in supplied.parts):
        raise ValueError("Artifact paths must remain relative to the workspace")

    candidate = root / supplied
    current = root
    for part in supplied.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlink paths are not allowed for artifact access")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("Artifact path must exist inside the active workspace") from exc
    if not resolved.is_file():
        raise ValueError("Artifact path must identify a regular file")
    return resolved


def list_workspace_artifacts(
    workspace: str | Path,
    *,
    max_entries: int = MAX_INVENTORY_ENTRIES,
    max_depth: int = MAX_INVENTORY_DEPTH,
) -> dict[str, Any]:
    """Return bounded metadata for regular files; file contents are never read."""
    if not 1 <= max_entries <= MAX_INVENTORY_ENTRIES:
        raise ValueError(f"max_entries must be between 1 and {MAX_INVENTORY_ENTRIES}")
    if not 1 <= max_depth <= MAX_INVENTORY_DEPTH:
        raise ValueError(f"max_depth must be between 1 and {MAX_INVENTORY_DEPTH}")

    root = _workspace_root(workspace)
    entries: list[dict[str, Any]] = []
    truncated = False

    def walk(directory: Path, depth: int) -> None:
        nonlocal truncated
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name.casefold())
        except OSError:
            return
        for child in children:
            if child.is_symlink():
                continue
            if child.is_dir():
                if depth < max_depth and child.name not in SKIPPED_DIRECTORIES:
                    walk(child, depth + 1)
                continue
            if not child.is_file():
                continue
            try:
                relative = child.relative_to(root).as_posix()
                size = child.stat().st_size
            except (OSError, ValueError):
                continue
            if len(entries) >= max_entries:
                truncated = True
                return
            entries.append({
                "path": relative,
                "name": child.name,
                "suffix": child.suffix.lower(),
                "size_bytes": size,
            })

    walk(root, 1)
    return {
        "workspace": ".",
        "entries": entries,
        "count": len(entries),
        "truncated": truncated,
        "max_depth": max_depth,
    }


def read_workspace_excerpt(
    workspace: str | Path,
    relative_path: str,
    *,
    start_line: int = 1,
    max_lines: int = MAX_EXCERPT_LINES,
    max_chars: int = MAX_EXCERPT_CHARS,
) -> dict[str, Any]:
    """Read a bounded UTF-8 excerpt with workspace-relative line provenance."""
    if start_line < 1:
        raise ValueError("start_line must be at least 1")
    if not 1 <= max_lines <= MAX_EXCERPT_LINES:
        raise ValueError(f"max_lines must be between 1 and {MAX_EXCERPT_LINES}")
    if not 1 <= max_chars <= MAX_EXCERPT_CHARS:
        raise ValueError(f"max_chars must be between 1 and {MAX_EXCERPT_CHARS}")

    root = _workspace_root(workspace)
    path = _resolve_workspace_file(root, relative_path)
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("Artifact exceeds the direct-read limit")

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError("Artifact must be a readable UTF-8 text file") from exc

    lines = content.splitlines()
    selected = lines[start_line - 1 : start_line - 1 + max_lines]
    excerpt = "\n".join(selected)
    truncated = start_line - 1 + len(selected) < len(lines)
    if len(excerpt) > max_chars:
        excerpt = excerpt[:max_chars]
        truncated = True

    end_line = start_line - 1 + len(selected)
    return {
        "path": path.relative_to(root).as_posix(),
        "start_line": start_line,
        "end_line": end_line,
        "content": excerpt,
        "truncated": truncated,
        "total_lines": len(lines),
        "size_bytes": path.stat().st_size,
    }
