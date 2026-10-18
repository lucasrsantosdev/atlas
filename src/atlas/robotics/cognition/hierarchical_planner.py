"""Bounded, side-effect-free hierarchical task decomposition for simulated robots."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class Task:
    name: str
    children: tuple['Task', ...] = ()
    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError('task name required')
        if not isinstance(self.children, tuple) or any(not isinstance(c, Task) for c in self.children):
            raise ValueError('children must be tasks')

@dataclass(frozen=True)
class TaskPlan:
    goal: str
    actions: tuple[str, ...]

class HierarchicalPlanner:
    """Only explicitly registered task graphs and allowlisted primitive actions."""
    def __init__(self, tasks: Mapping[str, Task], allowed_actions: set[str] | frozenset[str], *, max_depth: int = 12, max_actions: int = 64):
        if not 1 <= max_depth <= 64 or not 1 <= max_actions <= 1024:
            raise ValueError('invalid planning limits')
        if not allowed_actions or any(not isinstance(a, str) or not a for a in allowed_actions):
            raise ValueError('invalid action allowlist')
        self.tasks = dict(tasks)
        self.allowed_actions = frozenset(allowed_actions)
        self.max_depth, self.max_actions = max_depth, max_actions

    def plan(self, goal: str) -> TaskPlan:
        if goal not in self.tasks:
            raise ValueError('unknown goal')
        actions: list[str] = []
        visiting: set[int] = set()
        def visit(task: Task, depth: int) -> None:
            if depth > self.max_depth:
                raise ValueError('task depth exceeded')
            ident = id(task)
            if ident in visiting:
                raise ValueError('cyclic task graph')
            visiting.add(ident)
            try:
                if task.children:
                    for child in task.children:
                        visit(child, depth + 1)
                else:
                    if task.name not in self.allowed_actions:
                        raise ValueError('action not allowed: ' + task.name)
                    actions.append(task.name)
                    if len(actions) > self.max_actions:
                        raise ValueError('action budget exceeded')
            finally:
                visiting.remove(ident)
        visit(self.tasks[goal], 0)
        return TaskPlan(goal, tuple(actions))
