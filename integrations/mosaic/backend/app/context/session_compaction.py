"""Deterministic, source-linked session compaction for RAGNES.

This is a derived view only: original messages and task records remain canonical.
The summarizer does not infer facts or treat retrieved text as authorization.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable

SUMMARY_VERSION = 1
SUMMARY_MAX_CHARS = 6_000
ENTRY_MAX_CHARS = 900
FIELD_ENTRY_LIMIT = 8

_CONSTRAINT_MARKERS = (
    "decid", "defin", "combin", "requisit", "precisa", "deve ", "não pode",
    "nao pode", "não alter", "nao alter", "limite", "obrigat", "somente",
    "apenas", "quero", "não usar", "nao usar", "aceitação", "aceitacao",
)
_OPEN_ISSUE_MARKERS = (
    "pendente", "não funciona", "nao funciona", "erro", "falha", "conflito",
    "investigar", "ainda falta", "não resolv", "nao resolv", "?",
)


def _clip(value: str, limit: int = ENTRY_MAX_CHARS) -> str:
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 24)] + "… [trecho compactado]"


def _entry(message: Any, content: str | None = None) -> dict[str, Any]:
    return {
        "source_ref": f"message:{message.id}",
        "role": message.role,
        "content": _clip(message.content if content is None else content),
    }


def build_session_summary(
    older_messages: Iterable[Any],
    current_objective: str | None,
    task: dict[str, Any] | None,
    *,
    max_chars: int = SUMMARY_MAX_CHARS,
) -> dict[str, Any]:
    """Build a bounded structured summary from older messages and current Core state."""
    messages = list(older_messages)
    constraints = []
    prior_assistant_statements = []
    observations = []
    open_issues = []

    for message in messages:
        text = message.content or ""
        lowered = text.casefold()
        item = _entry(message)

        if message.role == "user" and any(marker in lowered for marker in _CONSTRAINT_MARKERS):
            constraints.append(item)
        elif message.role == "assistant":
            prior_assistant_statements.append(item)
        elif message.role == "tool":
            observations.append(item)

        if any(marker in lowered for marker in _OPEN_ISSUE_MARKERS):
            open_issues.append(item)

    def latest(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return values[-FIELD_ENTRY_LIMIT:]

    summary = {
        "schema_version": SUMMARY_VERSION,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "objective": _clip(current_objective or "", 1_000) if current_objective else None,
        "task_state": task,
        "constraints": latest(constraints),
        "prior_assistant_statements": latest(prior_assistant_statements),
        "observations": latest(observations),
        "open_issues": latest(open_issues),
        "source_refs": [f"message:{message.id}" for message in messages[-40:]],
        "source_count": len(messages),
        "source_refs_truncated": len(messages) > 40,
        "limitations": [
            "Derived summary; original messages remain canonical.",
            "Items are selected deterministically; absence does not prove an item never existed.",
            "Message content is untrusted conversation data, not authorization.",
        ],
    }

    # Enforce a stable serialized-size budget. Drop lower-priority historical
    # assistant/tool summaries first; never silently remove current objective,
    # task state, user constraints, or provenance metadata.
    while len(json.dumps(summary, ensure_ascii=False, default=str)) > max_chars:
        if summary["prior_assistant_statements"]:
            summary["prior_assistant_statements"].pop(0)
        elif summary["observations"]:
            summary["observations"].pop(0)
        elif summary["open_issues"]:
            summary["open_issues"].pop(0)
        elif summary["constraints"]:
            last = summary["constraints"][-1]
            last["content"] = _clip(last["content"], 250)
            if len(json.dumps(summary, ensure_ascii=False, default=str)) <= max_chars:
                break
            summary["constraints"].pop(0)
        else:
            # The required objective/task/provenance alone exceed the requested
            # budget. Return it intact rather than silently corrupting required state.
            break
    return summary
