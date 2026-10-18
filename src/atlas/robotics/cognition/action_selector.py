"""Rank only actions explicitly offered by a caller."""
from .experience_memory import ExperienceMemory

class ActionSelector:
    def __init__(self, memory: ExperienceMemory | None = None): self.memory=memory
    def select(self, intent: str, candidates: tuple[str,...]) -> str:
        if not candidates or any(not isinstance(c,str) or not c for c in candidates): raise ValueError("invalid candidates")
        if len(set(candidates))!=len(candidates): raise ValueError("duplicate candidates")
        def score(action):
            rate=self.memory.success_rate(intent,action) if self.memory else None
            return rate if rate is not None else 0.5
        return sorted(candidates,key=lambda action:(-score(action),candidates.index(action)))[0]
