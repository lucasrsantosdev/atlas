from __future__ import annotations

from atlas.knowledge.hybrid_retriever import (
    HybridSearchResult,
)


def build_rag_context(
    results: tuple[HybridSearchResult, ...],
    *,
    max_chars: int = 6000,
) -> str:
    """
    Constrói contexto documental híbrido para o modelo local.
    """

    if max_chars <= 0:
        raise ValueError(
            "max_chars deve ser maior que zero."
        )

    if not results:
        return (
            "Knowledge context:\n\n"
            "Nenhum trecho relevante foi encontrado "
            "na biblioteca local."
        )

    parts: list[str] = [
        "Knowledge context:",
        "",
        (
            "Os trechos abaixo foram recuperados "
            "da biblioteca local do Atlas."
        ),
        (
            "Use estes trechos como fontes locais "
            "para responder à pergunta."
        ),
        (
            "Não invente informações documentais "
            "que não estejam presentes nas fontes."
        ),
        (
            "Se o contexto for insuficiente, diga "
            "claramente que a biblioteca local "
            "não contém informação suficiente."
        ),
        "",
    ]

    current_size = sum(
        len(part)
        for part in parts
    )

    for result in results:
        semantic = (
            f"{result.semantic_score:.4f}"
            if result.semantic_score is not None
            else "N/A"
        )

        lexical = (
            f"{result.lexical_score:.4f}"
            if result.lexical_score is not None
            else "N/A"
        )

        block = (
            f"[Documento: {result.document_name}]\n"
            f"[Chunk: {result.chunk_index}]\n"
            f"[Semantic: {semantic}]\n"
            f"[Lexical: {lexical}]\n"
            f"[Fusion RRF: {result.fusion_score:.6f}]\n"
            f"{result.content.strip()}\n"
        )

        if (
            current_size + len(block)
            > max_chars
        ):
            break

        parts.append(block)
        parts.append("")

        current_size += len(block)

    return "\n".join(parts).strip()
