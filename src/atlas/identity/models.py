from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AtlasIdentity:
    name: str
    version: str
    agent_type: str
    created_at: str
    mission: str
    architecture: dict[str, bool]
    continuity: dict[str, bool]
    personality: dict[str, bool]
    preferences: dict[str, Any]
    principles: list[dict[str, Any]]
    capabilities: dict[str, dict[str, bool]]