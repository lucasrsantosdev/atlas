from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Model:
    id: int | None
    name: str
    provider: str
    model_name: str
    configuration: dict[str, Any]
    enabled: bool
