"""Bounded, opt-in in-memory feedback; not model training."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Experience:
    intent: str
    action: str
    success: bool

class ExperienceMemory:
    def __init__(self, capacity: int = 128):
        if not isinstance(capacity,int) or isinstance(capacity,bool) or capacity < 1: raise ValueError("invalid capacity")
        self.capacity=capacity
        self._records: list[Experience]=[]
    def record(self, item: Experience):
        if not isinstance(item, Experience): raise TypeError("expected Experience")
        self._records=(self._records+[item])[-self.capacity:]
    def success_rate(self, intent: str, action: str) -> float | None:
        matches=[x.success for x in self._records if x.intent==intent and x.action==action]
        return sum(matches)/len(matches) if matches else None
    def recent(self) -> tuple[Experience,...]: return tuple(self._records)
