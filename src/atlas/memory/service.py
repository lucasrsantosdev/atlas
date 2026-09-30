from __future__ import annotations

from typing import Any

from atlas.memory.models import (
    MemoryRecord,
    MemorySource,
    MemoryType,
    MemoryVerification,
)
from atlas.memory.store import JsonlMemoryStore


class MemoryService:
    """
    Camada de serviço da memória do Atlas.

    Responsabilidades:
    - criar registros de memória;
    - aplicar regras de autorização;
    - persistir registros;
    - centralizar futuras regras de memória.
    """

    def __init__(
        self,
        store: JsonlMemoryStore | None = None,
    ) -> None:
        self.store = store or JsonlMemoryStore()

    def remember(
        self,
        *,
        memory_type: MemoryType,
        content: str,
        source: MemorySource,
        authorized: bool,
        verification: MemoryVerification = MemoryVerification.UNVERIFIED,
        confidence: float = 1.0,
        tags: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        record = MemoryRecord.create(
            memory_type=memory_type,
            content=content,
            source=source,
            verification=verification,
            confidence=confidence,
            authorized=authorized,
            tags=tags,
            metadata=metadata,
        )

        self.store.save(record)

        return record
