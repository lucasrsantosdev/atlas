from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Project:
    id: int | None
    name: str
    description: str | None
    workspace: str
    metadata: dict[str, Any]
    state: dict[str, Any]
    created_at: str
    updated_at: str
