from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PEOPLE = "people"
    PROJECTS = "projects"
    DECISIONS = "decisions"
    LESSONS = "lessons"
    SKILLS = "skills"
    TIMELINE = "timeline"
    OBSERVATIONS = "observations"
    ARCHIVE = "archive"


class MemorySource(str, Enum):
    USER = "user"
    ATLAS = "atlas"
    SYSTEM = "system"
    IMPORT = "import"


class MemoryVerification(str, Enum):
    UNVERIFIED = "unverified"
    USER_CONFIRMED = "user_confirmed"
    SYSTEM_VERIFIED = "system_verified"
    INFERRED = "inferred"


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    memory_type: MemoryType
    content: str
    source: MemorySource
    created_at: str

    verification: MemoryVerification = MemoryVerification.UNVERIFIED
    confidence: float = 1.0
    authorized: bool = False

    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        memory_type: MemoryType,
        content: str,
        source: MemorySource,
        verification: MemoryVerification = MemoryVerification.UNVERIFIED,
        confidence: float = 1.0,
        authorized: bool = False,
        tags: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
    ) -> "MemoryRecord":
        clean_content = content.strip()

        if not clean_content:
            raise ValueError(
                "Conteúdo da memória não pode estar vazio."
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "Confidence deve estar entre 0.0 e 1.0."
            )

        return cls(
            id=str(uuid4()),
            memory_type=memory_type,
            content=clean_content,
            source=source,
            created_at=datetime.now(timezone.utc).isoformat(),
            verification=verification,
            confidence=confidence,
            authorized=authorized,
            tags=tags,
            metadata=metadata or {},
        )
