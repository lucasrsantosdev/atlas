from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Task:
    id: int | None
    conversation_id: int | None
    project_id: int | None
    type: str
    mode: str
    status: str
    plan: dict[str, Any] | None
    result: dict[str, Any] | None
    created_at: str
    updated_at: str
