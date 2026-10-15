from dataclasses import dataclass


@dataclass(frozen=True)
class Conversation:
    id: int | None
    title: str
    mode: str
    model_id: int
    project_id: int | None
    created_at: str
    updated_at: str
  