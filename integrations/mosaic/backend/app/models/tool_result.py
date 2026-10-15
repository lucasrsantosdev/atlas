from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    id: int | None
    tool_call_id: int
    status: str
    data: dict[str, Any] | None
    error: str | None
    created_at: str
