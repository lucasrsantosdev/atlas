from dataclasses import dataclass


@dataclass(frozen=True)
class Memory:
    id: int | None
    project_id: int | None
    type: str
    key: str
    value: str
    source: str
    confidence: float | None
    created_at: str
    updated_at: str
