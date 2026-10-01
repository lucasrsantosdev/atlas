from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntentType(str, Enum):
    QUESTION = "question"
    TASK = "task"
    COMMAND = "command"
    RETRIEVAL = "retrieval"
    MEMORY_REQUEST = "memory_request"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


class CapabilityType(str, Enum):
    FAST = "fast"
    REASONING = "reasoning"
    CODE = "code"
    SCIENCE = "science"
    ENGINEERING = "engineering"
    VISION = "vision"
    EMERGENCY = "emergency"


@dataclass(frozen=True)
class MosaicRequest:
    user_input: str
    session_id: str | None = None


@dataclass(frozen=True)
class ContextItem:
    content: str
    source: str
    relevance: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryCandidate:
    content: str
    memory_type: str
    importance: float
    reason: str


@dataclass(frozen=True)
class MosaicResult:
    intent: IntentType
    domain: str
    is_task: bool
    requires_context: bool
    entities: tuple[str, ...] = ()
    required_capabilities: tuple[CapabilityType, ...] = ()
    context: tuple[ContextItem, ...] = ()
    memory_candidates: tuple[MemoryCandidate, ...] = ()
