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
