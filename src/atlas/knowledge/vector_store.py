from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from atlas.knowledge.chunks import KnowledgeChunk


class VectorStoreError(RuntimeError):
    """Erro na camada de armazenamento vetorial."""


@dataclass(frozen=True)
class IndexedChunk:
    """
    Chunk associado ao seu vetor semântico.
    """

    chunk: KnowledgeChunk
    vector: tuple[float, ...]


@dataclass(frozen=True)
class VectorSearchResult:
    """
    Resultado de uma busca vetorial.
    """

    chunk: KnowledgeChunk
    score: float


class LocalVectorStore:
    """
    Vector Store local e em memória do Atlas.

    Não depende de banco vetorial externo.
    """

    def __init__(self) -> None:
        self._items: list[IndexedChunk] = []
        self._dimension: int | None = None

    @property
    def dimension(self) -> int | None:
        return self._dimension

    def __len__(self) -> int:
        return len(self._items)

    def add(
        self,
        *,
        chunk: KnowledgeChunk,
        vector: tuple[float, ...],
    ) -> None:
        if not vector:
            raise VectorStoreError(
                "Vetor não pode estar vazio."
            )

        if self._dimension is None:
            self._dimension = len(vector)

        elif len(vector) != self._dimension:
            raise VectorStoreError(
                "Dimensão do vetor incompatível com o Vector Store."
            )

        self._items.append(
            IndexedChunk(
                chunk=chunk,
                vector=vector,
            )
        )

    def add_many(
        self,
        items: tuple[IndexedChunk, ...],
    ) -> None:
        for item in items:
            self.add(
                chunk=item.chunk,
                vector=item.vector,
            )

    def search(
        self,
        *,
        query_vector: tuple[float, ...],
        limit: int = 5,
    ) -> tuple[VectorSearchResult, ...]:
        if limit <= 0:
            raise ValueError(
                "limit deve ser maior que zero."
            )

        if not query_vector:
            raise VectorStoreError(
                "Query vector não pode estar vazio."
            )

        if self._dimension is None:
            return ()

        if len(query_vector) != self._dimension:
            raise VectorStoreError(
                "Dimensão da consulta incompatível "
                "com o Vector Store."
            )

        results = [
            VectorSearchResult(
                chunk=item.chunk,
                score=self._cosine_similarity(
                    query_vector,
                    item.vector,
                ),
            )
            for item in self._items
        ]

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return tuple(
            results[:limit]
        )

    def clear(self) -> None:
        self._items.clear()
        self._dimension = None

    @staticmethod
    def _cosine_similarity(
        a: tuple[float, ...],
        b: tuple[float, ...],
    ) -> float:
        dot = sum(
            x * y
            for x, y in zip(a, b)
        )

        norm_a = sqrt(
            sum(x * x for x in a)
        )

        norm_b = sqrt(
            sum(y * y for y in b)
        )

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (
            norm_a * norm_b
        )
