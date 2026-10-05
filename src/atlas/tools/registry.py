from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from atlas.security import (
    Permission,
    PolicyEngine,
    RiskLevel,
)


@dataclass(frozen=True)
class ToolManifest:
    name: str
    description: str
    permission: Permission
    risk: RiskLevel = RiskLevel.LOW
    side_effects: bool = False


@dataclass(frozen=True)
class ToolResult:
    success: bool
    output: str


class ToolRegistry:
    """
    Registro central de ferramentas do Atlas.

    Nenhuma ferramenta registrada aqui deverá
    executar sem passar pelo PolicyEngine.
    """

    def __init__(
        self,
        policy: PolicyEngine,
    ) -> None:
        self.policy = policy

        self._tools: dict[
            str,
            tuple[
                ToolManifest,
                Callable[..., ToolResult],
            ],
        ] = {}

    def register(
        self,
        manifest: ToolManifest,
        handler: Callable[..., ToolResult],
    ) -> None:
        self._tools[
            manifest.name
        ] = (
            manifest,
            handler,
        )

    def execute(
        self,
        name: str,
        *,
        confirmed: bool = False,
        **kwargs,
    ) -> ToolResult:

        if name not in self._tools:
            return ToolResult(
                success=False,
                output=f"Unknown tool: {name}",
            )

        manifest, handler = self._tools[
            name
        ]

        decision = self.policy.evaluate(
            manifest.permission,
            manifest.risk,
        )

        if not decision.allowed:
            return ToolResult(
                success=False,
                output=decision.reason,
            )

        if (
            decision.requires_confirmation
            and not confirmed
        ):
            return ToolResult(
                success=False,
                output=(
                    "explicit confirmation required"
                ),
            )

        try:
            return handler(
                **kwargs
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                output=f"tool failed: {exc}",
            )

    def manifests(
        self,
    ) -> tuple[ToolManifest, ...]:

        return tuple(
            value[0]
            for value
            in self._tools.values()
        )
