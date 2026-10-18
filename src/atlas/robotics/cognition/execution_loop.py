"""Bounded symbolic cognitive execution loop. Never actuates physical hardware."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .hierarchical_planner import HierarchicalPlanner
from .decision_evaluator import Candidate, DecisionEvaluator
from .episodic_memory import Episode, EpisodicMemory

@dataclass(frozen=True)
class LoopResult:
    goal: str
    status: str
    attempted: tuple[str, ...]
    completed: tuple[str, ...]
    replans: int
    reason: str

class CognitiveExecutionLoop:
    """Observe via a supplied callback, choose authorized symbolic steps, learn outcomes.

    On a failure, optionally replace that step with a separately registered fallback.
    No fallback recursion; bounded by max_replans and max_steps. All effects are
    caller-supplied simulation callbacks; this class does not open any device.
    """
    def __init__(self, planner: HierarchicalPlanner, *, memory: EpisodicMemory | None = None,
                 evaluator: DecisionEvaluator | None = None, max_steps: int = 64,
                 max_replans: int = 2):
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= 1024:
            raise ValueError('invalid step budget')
        if isinstance(max_replans, bool) or not isinstance(max_replans, int) or not 0 <= max_replans <= 32:
            raise ValueError('invalid replan budget')
        self.planner = planner
        self.memory = memory if memory is not None else EpisodicMemory()
        self.evaluator = evaluator if evaluator is not None else DecisionEvaluator()
        self.max_steps, self.max_replans = max_steps, max_replans

    def run(self, goal: str, *, session: str, execute: Callable[[str], bool],
            observe: Callable[[], bool] | None = None,
            fallback: dict[str, tuple[str, ...]] | None = None,
            cancelled: Callable[[], bool] | None = None) -> LoopResult:
        if not isinstance(session, str) or not session.strip():
            raise ValueError('session required')
        if not callable(execute) or (observe is not None and not callable(observe)):
            raise TypeError('callbacks required')
        plan = self.planner.plan(goal)
        if len(plan.actions) > self.max_steps:
            return LoopResult(goal, 'budget_exceeded', (), (), 0, 'plan exceeds step budget')
        attempted: list[str] = []
        completed: list[str] = []
        replans = 0
        fallbacks = fallback or {}
        for action in plan.actions:
            if cancelled is not None and cancelled():
                return LoopResult(goal, 'cancelled', tuple(attempted), tuple(completed), replans, 'cancelled')
            if observe is not None and not observe():
                return LoopResult(goal, 'blocked', tuple(attempted), tuple(completed), replans, 'observation unsafe')
            candidates = (action,)
            alternatives = fallbacks.get(action, ())
            if not isinstance(alternatives, tuple):
                raise ValueError('fallbacks must be tuples')
            for alternative in alternatives:
                if alternative not in self.planner.allowed_actions:
                    raise ValueError('fallback not authorized')
            # Primary first; fallbacks are tried only after an observed failure.
            for attempt_action in candidates + alternatives:
                if attempt_action != action:
                    if replans >= self.max_replans:
                        break
                    replans += 1
                if len(attempted) >= self.max_steps:
                    return LoopResult(goal, 'budget_exceeded', tuple(attempted), tuple(completed), replans, 'step budget exhausted')
                if cancelled is not None and cancelled():
                    return LoopResult(goal, 'cancelled', tuple(attempted), tuple(completed), replans, 'cancelled')
                if observe is not None and not observe():
                    return LoopResult(goal, 'blocked', tuple(attempted), tuple(completed), replans, 'observation unsafe')
                attempted.append(attempt_action)
                try:
                    outcome = execute(attempt_action)
                    success = outcome is True
                except Exception:
                    success = False
                self.memory.record(Episode(session, goal, attempt_action, success, 1.0 if success else 0.0))
                if success:
                    completed.append(attempt_action)
                    break
            else:
                return LoopResult(goal, 'failed', tuple(attempted), tuple(completed), replans, f'failed: {action}')
            if not completed or completed[-1] != attempted[-1]:
                return LoopResult(goal, 'failed', tuple(attempted), tuple(completed), replans, f'failed: {action}')
        return LoopResult(goal, 'completed', tuple(attempted), tuple(completed), replans, 'all steps completed')
