from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Message:
    id: int | None
    conversation_id: int
    role: str
    content: str
    created_at: str
    metadata: dict[str, Any]
