"""Priority-based goals; no autonomous execution."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Goal:
    name: str
    priority: int = 0
    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip(): raise ValueError("goal name required")
        if isinstance(self.priority, bool) or not isinstance(self.priority, int): raise ValueError("invalid priority")

class GoalManager:
    def __init__(self): self._goals: dict[str, Goal] = {}
    def add(self, goal: Goal): self._goals[goal.name] = goal
    def remove(self, name: str): self._goals.pop(name, None)
    def next_goal(self) -> Goal | None:
        return sorted(self._goals.values(), key=lambda g: (-g.priority, g.name))[0] if self._goals else None
