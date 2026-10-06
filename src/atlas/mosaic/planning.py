from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class PlanRisk(str, Enum):
    LOW='low'; MEDIUM='medium'; HIGH='high'; CRITICAL='critical'

@dataclass(frozen=True)
class PlanStep:
    kind: str
    capability: str
    description: str
    tool: str | None = None

@dataclass(frozen=True)
class ExecutionPlan:
    goal: str
    complexity: str
    risk: PlanRisk
    needs_memory: bool
    needs_knowledge: bool
    capabilities: tuple[str, ...]
    steps: tuple[PlanStep, ...]
    max_steps: int = 8
    max_retries: int = 2
