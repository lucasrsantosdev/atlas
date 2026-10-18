"""Connect text-derived expression intentions to safe symbolic cognition plans."""
from __future__ import annotations
from dataclasses import dataclass
from .gesture_generator import GestureGenerator
from atlas.robotics.cognition.behavior_planner import BehaviorPlan

@dataclass(frozen=True)
class ExpressionDecision:
    text: str
    behavior: BehaviorPlan

class CognitiveExpression:
    def __init__(self, generator: GestureGenerator | None = None):
        self.generator = generator or GestureGenerator()

    def plan(self, text: str, joints: dict[str, float], *, safety=None) -> ExpressionDecision:
        if not isinstance(text, str) or not text.strip() or len(text) > 4000:
            raise ValueError('invalid expression text')
        return ExpressionDecision(text, self.generator.generate(text, joints, safety=safety))
