from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Action:
    id: int | None
    task_id: int
    type: str
    target: str | None
    payload: dict[str, Any]
    status: str
    result: dict[str, Any] | None
    created_at: str
    updated_at: str
