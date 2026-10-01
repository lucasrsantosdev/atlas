from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeDocument:
    """
    Documento local ingerido pela camada de conhecimento do Atlas.
    """

    path: Path
    name: str
    suffix: str
    content: str
    size_bytes: int

    @classmethod
    def from_text_file(
        cls,
        path: str | Path,
    ) -> "KnowledgeDocument":
        file_path = Path(path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(
                f"Documento não encontrado: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Caminho não representa um arquivo: {file_path}"
            )

        content = file_path.read_text(
            encoding="utf-8"
        )

        return cls(
            path=file_path,
            name=file_path.name,
            suffix=file_path.suffix.lower(),
            content=content,
            size_bytes=file_path.stat().st_size,
        )
