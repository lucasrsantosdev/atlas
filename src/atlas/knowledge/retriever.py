from __future__ import annotations

from atlas.knowledge.embeddings import EmbeddingProvider
from atlas.knowledge.vector_store import (
    LocalVectorStore,
    VectorSearchResult,
)


class KnowledgeRetriever:
    """
    Recupera chunks semanticamente relacionados a uma consulta.
    """

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: LocalVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[VectorSearchResult, ...]:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError(
                "Consulta não pode estar vazia."
            )

        query_embedding = (
            self.embedding_provider.embed_text(
                clean_query
            )
        )

        return self.vector_store.search(
            query_vector=query_embedding.vector,
            limit=limit,
        )
