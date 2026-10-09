from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from atlas.knowledge.chunks import (
    DocumentChunker,
    KnowledgeChunk,
)
from atlas.knowledge.context import build_rag_context
from atlas.knowledge.embeddings import (
    EmbeddingProvider,
    OllamaEmbeddingProvider,
)
from atlas.knowledge.hybrid_retriever import (
    HybridKnowledgeRetriever,
    HybridSearchResult,
)
from atlas.knowledge.ingestion import DocumentIngestor
from atlas.knowledge.lexical_index import (
    LexicalKnowledgeIndex,
)
from atlas.knowledge.retriever import (
    KnowledgeRetriever,
)
from atlas.knowledge.vector_store import (
    IndexedChunk,
    LocalVectorStore,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

DEFAULT_INDEX_PATH = (
    PROJECT_ROOT
    / "knowledge"
    / "local"
    / "vector_index.jsonl"
)


class KnowledgeServiceError(RuntimeError):
    """Erro na camada de conhecimento do Atlas."""


@dataclass(frozen=True)
class KnowledgeIndexReport:
    documents: int
    chunks: int
    paths: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgeStatus:
    indexed_documents: int
    indexed_chunks: int
    lexical_chunks: int
    dimension: int | None
    fts_available: bool
    index_path: str


class KnowledgeService:
    """
    Coordena ingestão, embeddings, busca híbrida
    e RAG local do Atlas.
    """

    SUPPORTED_SUFFIXES = frozenset(
        {
            ".txt",
            ".md",
        }
    )

    def __init__(
        self,
        *,
        ingestor: DocumentIngestor | None = None,
        chunker: DocumentChunker | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: LocalVectorStore | None = None,
        lexical_index: LexicalKnowledgeIndex | None = None,
        index_path: str | Path | None = None,
    ) -> None:
        self.ingestor = (
            ingestor
            if ingestor is not None
            else DocumentIngestor()
        )

        self.chunker = (
            chunker
            if chunker is not None
            else DocumentChunker(
                chunk_size=1000,
                overlap=150,
            )
        )

        self.embedding_provider = (
            embedding_provider
            if embedding_provider is not None
            else OllamaEmbeddingProvider()
        )

        self.vector_store = (
            vector_store
            if vector_store is not None
            else LocalVectorStore()
        )

        self.lexical_index = (
            lexical_index
            if lexical_index is not None
            else LexicalKnowledgeIndex()
        )

        self.semantic_retriever = (
            KnowledgeRetriever(
                embedding_provider=self.embedding_provider,
                vector_store=self.vector_store,
            )
        )

        self.retriever = (
            HybridKnowledgeRetriever(
                semantic_retriever=self.semantic_retriever,
                lexical_index=self.lexical_index,
            )
        )

        self.index_file_path = Path(
            index_path
            if index_path is not None
            else DEFAULT_INDEX_PATH
        ).resolve()

        self._indexed_paths: set[str] = set()

    def _discover(
        self,
        path: str | Path,
    ) -> tuple[Path, ...]:
        target = Path(path).resolve()

        if not target.exists():
            raise KnowledgeServiceError(
                f"Caminho não encontrado: {target}"
            )

        if target.is_file():
            if (
                target.suffix.lower()
                not in self.SUPPORTED_SUFFIXES
            ):
                raise KnowledgeServiceError(
                    "Formato não suportado: "
                    f"{target.suffix}"
                )

            return (target,)

        return tuple(
            sorted(
                candidate
                for candidate in target.rglob("*")
                if (
                    candidate.is_file()
                    and candidate.suffix.lower()
                    in self.SUPPORTED_SUFFIXES
                )
            )
        )

    def index_document(
        self,
        path: str | Path,
    ) -> int:
        document = self.ingestor.ingest(
            path
        )

        resolved_path = str(
            document.path.resolve()
        )

        if resolved_path in self._indexed_paths:
            return 0

        chunks = self.chunker.split(
            document
        )

        if not chunks:
            self._indexed_paths.add(
                resolved_path
            )

            return 0

        embeddings = (
            self.embedding_provider.embed_many(
                tuple(
                    chunk.content
                    for chunk in chunks
                )
            )
        )

        indexed = tuple(
            IndexedChunk(
                chunk=chunk,
                vector=embedding.vector,
            )
            for chunk, embedding
            in zip(
                chunks,
                embeddings,
            )
        )

        self.vector_store.add_many(
            indexed
        )

        self.lexical_index.add_many(
            chunks
        )

        self._indexed_paths.add(
            resolved_path
        )

        return len(chunks)

    def index_path(
        self,
        path: str | Path,
    ) -> KnowledgeIndexReport:
        documents = self._discover(
            path
        )

        total_chunks = 0
        indexed_paths: list[str] = []

        for document_path in documents:
            chunks = self.index_document(
                document_path
            )

            if chunks > 0:
                total_chunks += chunks

                indexed_paths.append(
                    str(document_path)
                )

        return KnowledgeIndexReport(
            documents=len(indexed_paths),
            chunks=total_chunks,
            paths=tuple(indexed_paths),
        )

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[HybridSearchResult, ...]:
        return self.retriever.search(
            query,
            limit=limit,
        )

    def build_context(
        self,
        query: str,
        *,
        limit: int = 5,
        max_chars: int = 6000,
    ) -> str:
        results = self.search(
            query,
            limit=limit,
        )

        return build_rag_context(
            results,
            max_chars=max_chars,
        )

    def status(
        self,
    ) -> KnowledgeStatus:
        return KnowledgeStatus(
            indexed_documents=len(
                self._indexed_paths
            ),
            indexed_chunks=len(
                self.vector_store
            ),
            lexical_chunks=len(
                self.lexical_index
            ),
            dimension=self.vector_store.dimension,
            fts_available=(
                self.lexical_index.fts_available
            ),
            index_path=str(
                self.index_file_path
            ),
        )

    def save_index(
        self,
    ) -> None:
        self.index_file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        model = getattr(
            self.embedding_provider,
            "model",
            "unknown",
        )

        with self.index_file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            for item in self.vector_store.all_items():
                payload = {
                    "model": model,
                    "chunk": {
                        "document_name": (
                            item.chunk.document_name
                        ),
                        "document_path": (
                            item.chunk.document_path
                        ),
                        "chunk_index": (
                            item.chunk.chunk_index
                        ),
                        "start_char": (
                            item.chunk.start_char
                        ),
                        "end_char": (
                            item.chunk.end_char
                        ),
                        "content": (
                            item.chunk.content
                        ),
                    },
                    "vector": list(
                        item.vector
                    ),
                }

                file.write(
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                    )
                )

                file.write("\n")

    def load_index(
        self,
    ) -> int:
        if not self.index_file_path.exists():
            return 0

        self.vector_store.clear()
        self._indexed_paths.clear()

        loaded = 0

        with self.index_file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            for line in file:
                clean_line = line.strip()

                if not clean_line:
                    continue

                payload = json.loads(
                    clean_line
                )

                chunk_data = payload[
                    "chunk"
                ]

                chunk = KnowledgeChunk(
                    document_name=chunk_data[
                        "document_name"
                    ],
                    document_path=chunk_data[
                        "document_path"
                    ],
                    chunk_index=int(
                        chunk_data[
                            "chunk_index"
                        ]
                    ),
                    start_char=int(
                        chunk_data[
                            "start_char"
                        ]
                    ),
                    end_char=int(
                        chunk_data[
                            "end_char"
                        ]
                    ),
                    content=chunk_data[
                        "content"
                    ],
                )

                vector = tuple(
                    float(value)
                    for value
                    in payload["vector"]
                )

                self.vector_store.add(
                    chunk=chunk,
                    vector=vector,
                )

                self.lexical_index.add(
                    chunk
                )

                self._indexed_paths.add(
                    str(
                        Path(
                            chunk.document_path
                        ).resolve()
                    )
                )

                loaded += 1

        return loaded
