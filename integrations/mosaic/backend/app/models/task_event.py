from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TaskEvent:
    id: int
    task_id: int
    conversation_id: int | None
    project_id: int | None
    tool_call_id: int | None
    action_id: int | None
    timestamp: str
    level: str
    component: str
    event_name: str
    message: str
    duration_ms: int | None
    status: str | None
    metadata: dict[str, Any]
