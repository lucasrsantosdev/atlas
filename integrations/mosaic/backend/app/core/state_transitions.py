from __future__ import annotations


TASK_TRANSITIONS = {
    "pending": {"planning", "executing", "failed", "cancelled"},
    "planning": {"executing", "awaiting_approval", "failed", "cancelled"},
    "awaiting_approval": {"executing", "failed", "cancelled"},
    "executing": {"planning", "awaiting_approval", "validating", "completed", "failed", "cancelled"},
    "validating": {"executing", "completed", "failed", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}

ACTION_TRANSITIONS = {
    "pending": {"approved", "rejected", "cancelled"},
    "approved": {"executing", "cancelled"},
    "executing": {"completed", "failed", "cancelled"},
    "completed": set(),
    "rejected": set(),
    "failed": set(),
    "cancelled": set(),
}

TOOL_CALL_TRANSITIONS = {
    "pending": {"approved", "rejected", "cancelled"},
    "approved": {"executing", "failed", "cancelled"},
    "executing": {"completed", "failed", "cancelled"},
    "completed": set(),
    "rejected": set(),
    "failed": set(),
    "cancelled": set(),
}


def validate_transition(entity: str, current: str, target: str, transitions: dict[str, set[str]]) -> None:
    if target not in transitions.get(current, set()):
        raise ValueError(f"Invalid {entity} transition: {current} -> {target}")
