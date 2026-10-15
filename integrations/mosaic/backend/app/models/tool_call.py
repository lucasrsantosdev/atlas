from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolCall:
    id: int | None
    conversation_id: int
    task_id: int | None
    tool_name: str
    arguments: dict[str, Any]
    status: str
    created_at: str
    updated_at: str
