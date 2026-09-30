from __future__ import annotations

from atlas.memory.models import MemoryRecord


def build_memory_context(
    memories: tuple[MemoryRecord, ...],
    *,
    max_memories: int = 10,
) -> str:
    """
    Constrói contexto textual a partir de memórias
    previamente recuperadas pelo Atlas.

    Não executa busca.
    Não altera memória.
    Não persiste dados.
    """

    if max_memories <= 0:
        raise ValueError(
            "max_memories deve ser maior que zero."
        )

    if not memories:
        return ""

    selected = memories[:max_memories]

    lines: list[str] = [
        "Relevant Atlas memories:",
        "",
    ]

    for memory in selected:
        lines.append(
            f"[{memory.memory_type.value}]"
        )
        lines.append(
            f"Content: {memory.content}"
        )
        lines.append(
            f"Source: {memory.source.value}"
        )
        lines.append(
            f"Verification: {memory.verification.value}"
        )
        lines.append(
            f"Confidence: {memory.confidence:.2f}"
        )

        if memory.tags:
            lines.append(
                "Tags: "
                + ", ".join(memory.tags)
            )

        lines.append("")

    lines.extend(
        [
            "Memory usage rules:",
            "- Treat memories as context, not absolute truth.",
            "- Respect verification and confidence levels.",
            "- Do not invent missing memory details.",
            "- Distinguish remembered information from inference.",
        ]
    )

    return "\n".join(lines).strip()
