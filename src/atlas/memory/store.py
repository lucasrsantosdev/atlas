from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from atlas.memory.models import (
    MemoryRecord,
    MemorySource,
    MemoryType,
    MemoryVerification,
)


class MemoryStoreError(RuntimeError):
    """Erro de persistência da memória do Atlas."""


class JsonlMemoryStore:
    """
    Armazenamento persistente local baseado em JSONL.

    Cada tipo de memória é armazenado em seu próprio diretório.

    Exemplo:

    memory/
      projects/
        memories.jsonl
    """

    def __init__(
        self,
        root_path: str | Path | None = None,
    ) -> None:
        self.root_path = (
            Path(root_path).expanduser().resolve()
            if root_path is not None
            else self._default_root()
        )

    @staticmethod
    def _default_root() -> Path:
        return (
            Path(__file__).resolve().parents[3]
            / "memory"
        )

    def _memory_dir(
        self,
        memory_type: MemoryType,
    ) -> Path:
        return self.root_path / memory_type.value

    def _memory_file(
        self,
        memory_type: MemoryType,
    ) -> Path:
        return (
            self._memory_dir(memory_type)
            / "memories.jsonl"
        )

    def _serialize(
        self,
        record: MemoryRecord,
    ) -> dict[str, Any]:
        data = asdict(record)

        data["memory_type"] = record.memory_type.value
        data["source"] = record.source.value
        data["verification"] = record.verification.value
        data["tags"] = list(record.tags)

        return data

    def _deserialize(
        self,
        data: dict[str, Any],
    ) -> MemoryRecord:
        try:
            return MemoryRecord(
                id=str(data["id"]),
                memory_type=MemoryType(
                    data["memory_type"]
                ),
                content=str(data["content"]),
                source=MemorySource(
                    data["source"]
                ),
                created_at=str(data["created_at"]),
                verification=MemoryVerification(
                    data["verification"]
                ),
                confidence=float(
                    data.get("confidence", 1.0)
                ),
                authorized=bool(
                    data.get("authorized", False)
                ),
                tags=tuple(
                    data.get("tags", [])
                ),
                metadata=dict(
                    data.get("metadata", {})
                ),
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise MemoryStoreError(
                f"Registro de memória inválido: {exc}"
            ) from exc

    def save(
        self,
        record: MemoryRecord,
    ) -> None:
        """
        Persiste uma memória autorizada.
        """

        if not record.authorized:
            raise MemoryStoreError(
                "Memória não autorizada não pode "
                "ser persistida."
            )

        memory_dir = self._memory_dir(
            record.memory_type
        )

        memory_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        memory_file = self._memory_file(
            record.memory_type
        )

        serialized = self._serialize(record)

        try:
            with memory_file.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(
                    json.dumps(
                        serialized,
                        ensure_ascii=False,
                    )
                )
                file.write("\n")

        except OSError as exc:
            raise MemoryStoreError(
                f"Não foi possível persistir memória: {exc}"
            ) from exc

    def load_all(
        self,
        memory_type: MemoryType,
    ) -> tuple[MemoryRecord, ...]:
        """
        Carrega todas as memórias de um único tipo.
        """

        memory_file = self._memory_file(
            memory_type
        )

        if not memory_file.exists():
            return ()

        records: list[MemoryRecord] = []

        try:
            with memory_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                for line_number, line in enumerate(
                    file,
                    start=1,
                ):
                    clean_line = line.strip()

                    if not clean_line:
                        continue

                    try:
                        data = json.loads(
                            clean_line
                        )

                    except json.JSONDecodeError as exc:
                        raise MemoryStoreError(
                            "JSON inválido em "
                            f"{memory_file}, "
                            f"linha {line_number}: {exc}"
                        ) from exc

                    if not isinstance(data, dict):
                        raise MemoryStoreError(
                            "Registro inválido em "
                            f"{memory_file}, "
                            f"linha {line_number}."
                        )

                    records.append(
                        self._deserialize(data)
                    )

        except OSError as exc:
            raise MemoryStoreError(
                f"Não foi possível ler memória: {exc}"
            ) from exc

        return tuple(records)

    def load_everything(
        self,
    ) -> tuple[MemoryRecord, ...]:
        """
        Carrega memórias de todas as categorias conhecidas.
        """

        records: list[MemoryRecord] = []

        for memory_type in MemoryType:
            records.extend(
                self.load_all(memory_type)
            )

        return tuple(records)

    def get_by_id(
        self,
        memory_id: str,
    ) -> MemoryRecord | None:
        """
        Procura uma memória pelo identificador único.
        """

        clean_id = memory_id.strip()

        if not clean_id:
            raise ValueError(
                "ID da memória não pode estar vazio."
            )

        for record in self.load_everything():
            if record.id == clean_id:
                return record

        return None

    def search_text(
        self,
        query: str,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        """
        Busca textual simples, case-insensitive.

        Nesta etapa não utiliza embeddings ou banco vetorial.
        """

        clean_query = query.strip().casefold()

        if not clean_query:
            raise ValueError(
                "Consulta de memória não pode estar vazia."
            )

        self._validate_limit(limit)

        records = (
            self.load_all(memory_type)
            if memory_type is not None
            else self.load_everything()
        )

        matches = [
            record
            for record in records
            if clean_query in record.content.casefold()
        ]

        matches.sort(
            key=lambda record: record.created_at,
            reverse=True,
        )

        return tuple(matches[:limit])

    def search_tags(
        self,
        tags: tuple[str, ...],
        *,
        memory_type: MemoryType | None = None,
        match_all: bool = True,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        """
        Busca memória pelas tags associadas.
        """

        clean_tags = {
            tag.strip().casefold()
            for tag in tags
            if tag.strip()
        }

        if not clean_tags:
            raise ValueError(
                "Informe pelo menos uma tag."
            )

        self._validate_limit(limit)

        records = (
            self.load_all(memory_type)
            if memory_type is not None
            else self.load_everything()
        )

        matches: list[MemoryRecord] = []

        for record in records:
            record_tags = {
                tag.casefold()
                for tag in record.tags
            }

            if match_all:
                matched = clean_tags.issubset(
                    record_tags
                )
            else:
                matched = bool(
                    clean_tags.intersection(
                        record_tags
                    )
                )

            if matched:
                matches.append(record)

        matches.sort(
            key=lambda record: record.created_at,
            reverse=True,
        )

        return tuple(matches[:limit])

    def recent(
        self,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        """
        Recupera as memórias mais recentes.
        """

        self._validate_limit(limit)

        records = list(
            self.load_all(memory_type)
            if memory_type is not None
            else self.load_everything()
        )

        records.sort(
            key=lambda record: record.created_at,
            reverse=True,
        )

        return tuple(records[:limit])

    @staticmethod
    def _validate_limit(
        limit: int,
    ) -> None:
        if limit <= 0:
            raise ValueError(
                "Limit deve ser maior que zero."
            )
