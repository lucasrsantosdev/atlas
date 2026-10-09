from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from atlas.knowledge.chunks import KnowledgeChunk


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

DEFAULT_LEXICAL_DB = (
    PROJECT_ROOT
    / "knowledge"
    / "local"
    / "atlas_knowledge.db"
)


class LexicalIndexError(RuntimeError):
    """Erro na camada lexical de conhecimento."""


@dataclass(frozen=True)
class LexicalSearchResult:
    document_name: str
    document_path: str
    chunk_index: int
    content: str
    score: float


class LexicalKnowledgeIndex:
    """
    Índice lexical local usando SQLite + FTS5.

    Caso FTS5 não esteja disponível, utiliza busca LIKE.
    """

    def __init__(
        self,
        path: str | Path | None = None,
    ) -> None:
        self.path = Path(
            path
            if path is not None
            else DEFAULT_LEXICAL_DB
        ).resolve()

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._fts_available = False

        self._initialize()

    @property
    def fts_available(self) -> bool:
        return self._fts_available

    def _connect(
        self,
    ) -> sqlite3.Connection:
        return sqlite3.connect(
            self.path
        )

    def _initialize(
        self,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_name TEXT NOT NULL,
                    document_path TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

            try:
                connection.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
                    USING fts5(
                        chunk_id UNINDEXED,
                        content
                    )
                    """
                )

                self._fts_available = True

            except sqlite3.OperationalError:
                self._fts_available = False

    @staticmethod
    def _chunk_id(
        chunk: KnowledgeChunk,
    ) -> str:
        return (
            f"{chunk.document_path}"
            f"::{chunk.chunk_index}"
        )

    def add(
        self,
        chunk: KnowledgeChunk,
        *,
        metadata: dict | None = None,
    ) -> None:
        chunk_id = self._chunk_id(
            chunk
        )

        metadata_json = json.dumps(
            metadata or {},
            ensure_ascii=False,
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO chunks (
                    chunk_id,
                    document_name,
                    document_path,
                    chunk_index,
                    content,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT(chunk_id)
                DO UPDATE SET
                    document_name = excluded.document_name,
                    document_path = excluded.document_path,
                    chunk_index = excluded.chunk_index,
                    content = excluded.content,
                    metadata = excluded.metadata
                """,
                (
                    chunk_id,
                    chunk.document_name,
                    chunk.document_path,
                    chunk.chunk_index,
                    chunk.content,
                    metadata_json,
                ),
            )

            if self._fts_available:
                connection.execute(
                    """
                    DELETE FROM chunks_fts
                    WHERE chunk_id = ?
                    """,
                    (chunk_id,),
                )

                connection.execute(
                    """
                    INSERT INTO chunks_fts (
                        chunk_id,
                        content
                    )
                    VALUES (?, ?)
                    """,
                    (
                        chunk_id,
                        chunk.content,
                    ),
                )

    def add_many(
        self,
        chunks: tuple[KnowledgeChunk, ...],
    ) -> None:
        for chunk in chunks:
            self.add(
                chunk
            )

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[LexicalSearchResult, ...]:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError(
                "Consulta lexical não pode estar vazia."
            )

        if limit <= 0:
            raise ValueError(
                "limit deve ser maior que zero."
            )

        if self._fts_available:
            try:
                return self._search_fts(
                    clean_query,
                    limit=limit,
                )

            except sqlite3.OperationalError:
                pass

        return self._search_like(
            clean_query,
            limit=limit,
        )

    def _search_fts(
        self,
        query: str,
        *,
        limit: int,
    ) -> tuple[LexicalSearchResult, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    c.document_name,
                    c.document_path,
                    c.chunk_index,
                    c.content,
                    bm25(chunks_fts)
                FROM chunks_fts
                JOIN chunks c
                    USING(chunk_id)
                WHERE chunks_fts MATCH ?
                ORDER BY bm25(chunks_fts)
                LIMIT ?
                """,
                (
                    query,
                    limit,
                ),
            ).fetchall()

        return tuple(
            LexicalSearchResult(
                document_name=row[0],
                document_path=row[1],
                chunk_index=int(row[2]),
                content=row[3],
                score=-float(row[4]),
            )
            for row in rows
        )

    def _search_like(
        self,
        query: str,
        *,
        limit: int,
    ) -> tuple[LexicalSearchResult, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    document_name,
                    document_path,
                    chunk_index,
                    content
                FROM chunks
                WHERE content LIKE ?
                LIMIT ?
                """,
                (
                    f"%{query}%",
                    limit,
                ),
            ).fetchall()

        return tuple(
            LexicalSearchResult(
                document_name=row[0],
                document_path=row[1],
                chunk_index=int(row[2]),
                content=row[3],
                score=1.0,
            )
            for row in rows
        )

    def __len__(
        self,
    ) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM chunks"
            ).fetchone()

        return int(
            row[0]
            if row is not None
            else 0
        )
