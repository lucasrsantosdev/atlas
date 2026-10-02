from __future__ import annotations

from typing import Any

from atlas.memory.authorization import (
    MemoryAuthorizationError,
    MemoryAuthorizationPolicy,
)
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
    - avaliar autorização;
    - criar registros;
    - persistir registros;
    - recuperar memórias;
    - centralizar regras de memória.
    """

    def __init__(
        self,
        store: Any | None = None,
        authorization_policy: MemoryAuthorizationPolicy | None = None,
    ) -> None:
        self.store = store or JsonlMemoryStore()

        self.authorization_policy = (
            authorization_policy
            or MemoryAuthorizationPolicy()
        )

    def remember(
        self,
        *,
        memory_type: MemoryType,
        content: str,
        source: MemorySource,
        explicit_user_authorization: bool = False,
        system_owned: bool = False,
        verification: MemoryVerification = MemoryVerification.UNVERIFIED,
        confidence: float = 1.0,
        tags: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
    ) -> MemoryRecord:

        authorization = (
            self.authorization_policy.evaluate(
                memory_type=memory_type,
                source=source,
                explicit_user_authorization=(
                    explicit_user_authorization
                ),
                system_owned=system_owned,
            )
        )

        if not authorization.allowed:
            raise MemoryAuthorizationError(
                authorization.detail
            )

        final_metadata = dict(
            metadata or {}
        )

        final_metadata["authorization"] = {
            "reason": authorization.reason.value,
            "detail": authorization.detail,
        }

        record = MemoryRecord.create(
            memory_type=memory_type,
            content=content,
            source=source,
            verification=verification,
            confidence=confidence,
            authorized=True,
            tags=tags,
            metadata=final_metadata,
        )

        self.store.save(record)

        return record

    def recall_by_id(
        self,
        memory_id: str,
    ) -> MemoryRecord | None:
        return self.store.get_by_id(
            memory_id
        )

    def recall_text(
        self,
        query: str,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        return self.store.search_text(
            query,
            memory_type=memory_type,
            limit=limit,
        )

    def recall_tags(
        self,
        tags: tuple[str, ...],
        *,
        memory_type: MemoryType | None = None,
        match_all: bool = True,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        return self.store.search_tags(
            tags,
            memory_type=memory_type,
            match_all=match_all,
            limit=limit,
        )

    def recall_recent(
        self,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        return self.store.recent(
            memory_type=memory_type,
            limit=limit,
        )
