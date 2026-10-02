from __future__ import annotations

from atlas.knowledge.vector_store import (
    VectorSearchResult,
)


def build_rag_context(
    results: tuple[VectorSearchResult, ...],
    *,
    max_chars: int = 6000,
) -> str:
    """
    Constrói contexto documental para o modelo local.
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
            "Use os trechos abaixo como fontes locais "
            "para responder à pergunta."
        ),
        (
            "Não invente informações que não estejam "
            "presentes nas fontes quando a pergunta "
            "depender destes documentos."
        ),
        (
            "Se as fontes forem insuficientes, diga "
            "claramente que a biblioteca local não "
            "contém informação suficiente."
        ),
        "",
    ]

    current_size = sum(
        len(part)
        for part in parts
    )

    for result in results:
        block = (
            f"[Documento: {result.chunk.document_name}]\n"
            f"[Chunk: {result.chunk.chunk_index}]\n"
            f"[Similaridade: {result.score:.4f}]\n"
            f"{result.chunk.content.strip()}\n"
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
