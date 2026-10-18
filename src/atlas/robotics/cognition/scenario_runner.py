"""Deterministic dry-run scenarios, with fault injection and no hardware I/O."""
from __future__ import annotations
from dataclasses import dataclass
from .hierarchical_planner import HierarchicalPlanner

@dataclass(frozen=True)
class ScenarioResult:
    goal: str
    attempted: tuple[str, ...]
    completed: tuple[str, ...]
    status: str
    failure: str | None = None

class ScenarioRunner:
    """Executes *symbolic* actions only; it never invokes a robot controller."""
    def __init__(self, planner: HierarchicalPlanner):
        self.planner = planner

    def run(self, goal: str, *, fail_at: int | None = None, cancel_at: int | None = None) -> ScenarioResult:
        if any(x is not None and (isinstance(x, bool) or not isinstance(x, int) or x < 0)
               for x in (fail_at, cancel_at)):
            raise ValueError('invalid fault index')
        plan = self.planner.plan(goal)
        attempted, completed = [], []
        for i, action in enumerate(plan.actions):
            if cancel_at == i:
                return ScenarioResult(goal, tuple(attempted), tuple(completed), 'cancelled')
            attempted.append(action)
            if fail_at == i:
                return ScenarioResult(goal, tuple(attempted), tuple(completed), 'failed', f'injected fault at step {i}')
            completed.append(action)
        return ScenarioResult(goal, tuple(attempted), tuple(completed), 'completed')
