from __future__ import annotations

from atlas.core.status import (
    AtlasSystemStatus,
    ComponentState,
    ComponentStatus,
    SystemState,
)


class ComponentRegistry:
    """
    Registro central dos componentes conhecidos pelo Atlas Core.
    """

    def __init__(self) -> None:
        self._components: dict[str, ComponentStatus] = {}

    def register(
        self,
        name: str,
        state: ComponentState,
        *,
        critical: bool,
        detail: str = "",
    ) -> None:
        self._components[name] = ComponentStatus(
            name=name,
            state=state,
            critical=critical,
            detail=detail,
        )

    def get(self, name: str) -> ComponentStatus | None:
        return self._components.get(name)

    def all(self) -> tuple[ComponentStatus, ...]:
        return tuple(self._components.values())

    def system_status(self) -> AtlasSystemStatus:
        components = self.all()

        critical_failure = any(
            component.critical
            and component.state
            not in {
                ComponentState.READY,
                ComponentState.DISABLED,
            }
            for component in components
        )

        degraded = any(
            component.state
            in {
                ComponentState.DEGRADED,
                ComponentState.UNAVAILABLE,
            }
            for component in components
        )

        if critical_failure:
            state = SystemState.ERROR
        elif degraded:
            state = SystemState.DEGRADED
        else:
            state = SystemState.READY

        return AtlasSystemStatus(
            state=state,
            components=components,
        )