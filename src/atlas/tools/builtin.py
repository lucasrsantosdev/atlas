from __future__ import annotations

from pathlib import Path

from atlas.security import (
    Permission,
    RiskLevel,
)

from atlas.tools.registry import (
    ToolManifest,
    ToolRegistry,
    ToolResult,
)


def register_safe_filesystem(
    registry: ToolRegistry,
    root: str | Path,
) -> None:
    """
    Registra ferramentas de leitura e escrita
    limitadas a um workspace autorizado.
    """

    root_path = Path(
        root
    ).resolve()

    def resolve(
        path: str,
    ) -> Path:

        target = (
            root_path
            / path
        ).resolve()

        if (
            target != root_path
            and root_path
            not in target.parents
        ):
            raise ValueError(
                "path escapes allowed workspace"
            )

        return target

    def read(
        path: str,
    ) -> ToolResult:

        target = resolve(
            path
        )

        content = target.read_text(
            encoding="utf-8"
        )

        return ToolResult(
            success=True,
            output=content,
        )

    registry.register(
        ToolManifest(
            name="filesystem.read",
            description=(
                "Read UTF-8 text "
                "inside authorized workspace"
            ),
            permission=Permission.READ_FILE,
            risk=RiskLevel.LOW,
            side_effects=False,
        ),
        read,
    )

    def write(
        path: str,
        content: str,
    ) -> ToolResult:

        target = resolve(
            path
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            content,
            encoding="utf-8",
        )

        return ToolResult(
            success=True,
            output=str(target),
        )

    registry.register(
        ToolManifest(
            name="filesystem.write",
            description=(
                "Write UTF-8 text "
                "inside authorized workspace"
            ),
            permission=Permission.WRITE_FILE,
            risk=RiskLevel.HIGH,
            side_effects=True,
        ),
        write,
    )
