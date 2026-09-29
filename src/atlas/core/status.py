from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ComponentState(str, Enum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"


class SystemState(str, Enum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ComponentStatus:
    name: str
    state: ComponentState
    critical: bool
    detail: str = ""


@dataclass(frozen=True)
class AtlasSystemStatus:
    state: SystemState
    components: tuple[ComponentStatus, ...]

    @property
    def ready_components(self) -> int:
        return sum(
            1
            for component in self.components
            if component.state == ComponentState.READY
        )

    @property
    def total_components(self) -> int:
        return len(self.components)