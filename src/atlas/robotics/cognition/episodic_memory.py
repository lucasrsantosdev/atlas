"""Session-isolated bounded episodes and outcome statistics (no online model training)."""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Episode:
    session: str
    goal: str
    action: str
    success: bool
    reward: float
    def __post_init__(self):
        if any(not isinstance(x, str) or not x.strip() for x in (self.session, self.goal, self.action)):
            raise ValueError('session, goal and action required')
        if not isinstance(self.success, bool) or isinstance(self.reward, bool) or not isinstance(self.reward, (int, float)) or not math.isfinite(self.reward):
            raise ValueError('invalid episode outcome')

class EpisodicMemory:
    def __init__(self, capacity: int = 256):
        if isinstance(capacity, bool) or not isinstance(capacity, int) or not 1 <= capacity <= 100000:
            raise ValueError('invalid capacity')
        self.capacity = capacity
        self._episodes: list[Episode] = []

    def record(self, episode: Episode) -> None:
        if not isinstance(episode, Episode):
            raise TypeError('expected Episode')
        self._episodes.append(episode)
        if len(self._episodes) > self.capacity:
            del self._episodes[:len(self._episodes) - self.capacity]

    def recent(self, session: str) -> tuple[Episode, ...]:
        return tuple(e for e in self._episodes if e.session == session)

    def stats(self, session: str, goal: str, action: str) -> tuple[int, float, float]:
        matched = [e for e in self._episodes if (e.session, e.goal, e.action) == (session, goal, action)]
        if not matched:
            return (0, 0.0, 0.0)
        return (len(matched), sum(e.success for e in matched) / len(matched), sum(e.reward for e in matched) / len(matched))
