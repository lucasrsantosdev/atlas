from __future__ import annotations

from pathlib import Path

from atlas.knowledge.documents import KnowledgeDocument


class DocumentIngestionError(RuntimeError):
    """Erro durante ingestão documental."""


class DocumentIngestor:
    """
    Ingestor documental local do Atlas.

    Nesta primeira versão, aceita documentos textuais UTF-8.
    """

    SUPPORTED_SUFFIXES = frozenset(
        {
            ".txt",
            ".md",
        }
    )

    def ingest(
        self,
        path: str | Path,
    ) -> KnowledgeDocument:
        file_path = Path(path).resolve()

        if file_path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
            raise DocumentIngestionError(
                f"Formato ainda não suportado: {file_path.suffix}"
            )

        try:
            return KnowledgeDocument.from_text_file(
                file_path
            )

        except (
            OSError,
            UnicodeError,
            ValueError,
        ) as exc:
            raise DocumentIngestionError(
                f"Falha ao ingerir documento '{file_path}': {exc}"
            ) from exc
