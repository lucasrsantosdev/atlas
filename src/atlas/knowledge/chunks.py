from __future__ import annotations

from dataclasses import dataclass

from atlas.knowledge.documents import KnowledgeDocument


@dataclass(frozen=True)
class KnowledgeChunk:
    """
    Fragmento de um documento da biblioteca do Atlas.
    """

    document_name: str
    document_path: str
    chunk_index: int
    start_char: int
    end_char: int
    content: str


class DocumentChunker:
    """
    Divide documentos em fragmentos parcialmente sobrepostos.

    O overlap ajuda a preservar contexto entre dois chunks
    consecutivos.
    """

    def __init__(
        self,
        *,
        chunk_size: int = 1000,
        overlap: int = 150,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size deve ser maior que zero."
            )

        if overlap < 0:
            raise ValueError(
                "overlap não pode ser negativo."
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap deve ser menor que chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(
        self,
        document: KnowledgeDocument,
    ) -> tuple[KnowledgeChunk, ...]:
        content = document.content

        if not content.strip():
            return ()

        chunks: list[KnowledgeChunk] = []

        start = 0
        index = 0
        content_length = len(content)

        while start < content_length:
            end = min(
                start + self.chunk_size,
                content_length,
            )

            chunk_content = content[start:end]

            chunks.append(
                KnowledgeChunk(
                    document_name=document.name,
                    document_path=str(document.path),
                    chunk_index=index,
                    start_char=start,
                    end_char=end,
                    content=chunk_content,
                )
            )

            if end >= content_length:
                break

            start = end - self.overlap
            index += 1

        return tuple(chunks)
