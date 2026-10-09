from __future__ import annotations

from dataclasses import dataclass

from atlas.knowledge.lexical_index import (
    LexicalKnowledgeIndex,
)
from atlas.knowledge.retriever import (
    KnowledgeRetriever,
)
from atlas.knowledge.vector_store import (
    VectorSearchResult,
)


@dataclass(frozen=True)
class HybridSearchResult:
    document_name: str
    document_path: str
    chunk_index: int
    content: str
    semantic_score: float | None
    lexical_score: float | None
    fusion_score: float


class HybridKnowledgeRetriever:
    """
    Combina busca semântica e lexical usando
    Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        *,
        semantic_retriever: KnowledgeRetriever,
        lexical_index: LexicalKnowledgeIndex,
        rrf_k: int = 60,
    ) -> None:
        if rrf_k <= 0:
            raise ValueError(
                "rrf_k deve ser maior que zero."
            )

        self.semantic_retriever = (
            semantic_retriever
        )

        self.lexical_index = (
            lexical_index
        )

        self.rrf_k = rrf_k

    @staticmethod
    def _key(
        document_path: str,
        chunk_index: int,
    ) -> tuple[str, int]:
        return (
            document_path,
            chunk_index,
        )

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        candidate_limit: int = 10,
    ) -> tuple[HybridSearchResult, ...]:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError(
                "Consulta híbrida não pode estar vazia."
            )

        if limit <= 0:
            raise ValueError(
                "limit deve ser maior que zero."
            )

        if candidate_limit <= 0:
            raise ValueError(
                "candidate_limit deve ser maior que zero."
            )

        semantic_results = (
            self.semantic_retriever.search(
                clean_query,
                limit=candidate_limit,
            )
        )

        lexical_results = (
            self.lexical_index.search(
                clean_query,
                limit=candidate_limit,
            )
        )

        combined: dict[
            tuple[str, int],
            dict,
        ] = {}

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            key = self._key(
                result.chunk.document_path,
                result.chunk.chunk_index,
            )

            entry = combined.setdefault(
                key,
                {
                    "document_name": (
                        result.chunk.document_name
                    ),
                    "document_path": (
                        result.chunk.document_path
                    ),
                    "chunk_index": (
                        result.chunk.chunk_index
                    ),
                    "content": (
                        result.chunk.content
                    ),
                    "semantic_score": None,
                    "lexical_score": None,
                    "fusion_score": 0.0,
                },
            )

            entry["semantic_score"] = (
                result.score
            )

            entry["fusion_score"] += (
                1.0
                / (self.rrf_k + rank)
            )

        for rank, result in enumerate(
            lexical_results,
            start=1,
        ):
            key = self._key(
                result.document_path,
                result.chunk_index,
            )

            entry = combined.setdefault(
                key,
                {
                    "document_name": (
                        result.document_name
                    ),
                    "document_path": (
                        result.document_path
                    ),
                    "chunk_index": (
                        result.chunk_index
                    ),
                    "content": (
                        result.content
                    ),
                    "semantic_score": None,
                    "lexical_score": None,
                    "fusion_score": 0.0,
                },
            )

            entry["lexical_score"] = (
                result.score
            )

            entry["fusion_score"] += (
                1.0
                / (self.rrf_k + rank)
            )

        ranked = sorted(
            combined.values(),
            key=lambda item: item[
                "fusion_score"
            ],
            reverse=True,
        )

        return tuple(
            HybridSearchResult(
                document_name=item[
                    "document_name"
                ],
                document_path=item[
                    "document_path"
                ],
                chunk_index=item[
                    "chunk_index"
                ],
                content=item[
                    "content"
                ],
                semantic_score=item[
                    "semantic_score"
                ],
                lexical_score=item[
                    "lexical_score"
                ],
                fusion_score=item[
                    "fusion_score"
                ],
            )
            for item in ranked[:limit]
        )
