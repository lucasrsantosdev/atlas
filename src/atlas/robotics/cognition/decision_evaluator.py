"""Auditable, deterministic decision evaluation. No motor execution."""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Candidate:
    action: str
    expected_reward: float
    risk: float
    duration_seconds: float
    def __post_init__(self):
        if not isinstance(self.action, str) or not self.action.strip():
            raise ValueError('action required')
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
               for v in (self.expected_reward, self.risk, self.duration_seconds)):
            raise ValueError('nonfinite decision inputs')
        if not 0 <= self.risk <= 1 or self.duration_seconds < 0:
            raise ValueError('invalid risk or duration')

@dataclass(frozen=True)
class Decision:
    action: str
    score: float
    reason: str

class DecisionEvaluator:
    def __init__(self, *, max_risk: float = 0.25, risk_penalty: float = 2.0, time_penalty: float = 0.01):
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) or v < 0
               for v in (max_risk, risk_penalty, time_penalty)) or max_risk > 1:
            raise ValueError('invalid decision policy')
        self.max_risk, self.risk_penalty, self.time_penalty = max_risk, risk_penalty, time_penalty

    def choose(self, candidates: tuple[Candidate, ...], *, allowed_actions: frozenset[str]) -> Decision:
        eligible = [c for c in candidates if c.action in allowed_actions and c.risk <= self.max_risk]
        if not eligible:
            raise ValueError('no safe authorized candidate')
        scored = [(c.expected_reward - self.risk_penalty * c.risk - self.time_penalty * c.duration_seconds, i, c)
                  for i, c in enumerate(eligible)]
        score, _, winner = max(scored, key=lambda x: (x[0], -x[1]))
        return Decision(winner.action, score, f'authorized; risk={winner.risk:.3f}; duration={winner.duration_seconds:.3f}s')
