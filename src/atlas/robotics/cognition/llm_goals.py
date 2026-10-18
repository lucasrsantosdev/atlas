"""Strict validation boundary for LLM-generated goals. No raw actuator commands."""
from __future__ import annotations
from dataclasses import dataclass
import json
import math
from typing import Protocol

class TextModel(Protocol):
    def generate(self, prompt: str) -> str: ...

@dataclass(frozen=True)
class GoalProposal:
    goal: str
    confidence: float
    reason: str

class LLMGoalAdapter:
    """LLM suggests a registered goal; local policy remains authoritative."""
    def __init__(self, model: TextModel, allowed_goals: frozenset[str], *, min_confidence: float = 0.5):
        if not allowed_goals or any(not isinstance(g, str) or not g for g in allowed_goals):
            raise ValueError('allowed goals required')
        if isinstance(min_confidence, bool) or not isinstance(min_confidence, (float, int)) or not math.isfinite(min_confidence) or not 0 <= min_confidence <= 1:
            raise ValueError('invalid confidence threshold')
        self.model, self.allowed_goals, self.min_confidence = model, allowed_goals, min_confidence

    def propose(self, user_text: str) -> GoalProposal:
        if not isinstance(user_text, str) or not user_text.strip() or len(user_text) > 2000:
            raise ValueError('invalid user text')
        prompt = ('Choose exactly one goal from this allowlist: ' + ', '.join(sorted(self.allowed_goals)) +
                  '. Respond ONLY with JSON object keys goal, confidence, reason. ' +
                  'Do not emit motor positions or commands. User request: ' + json.dumps(user_text))
        response = self.model.generate(prompt)
        if not isinstance(response, str) or len(response) > 4096:
            raise ValueError('invalid model response')
        try:
            obj = json.loads(response)
        except (ValueError, TypeError) as exc:
            raise ValueError('model did not return valid JSON') from exc
        if not isinstance(obj, dict) or set(obj) != {'goal', 'confidence', 'reason'}:
            raise ValueError('unexpected proposal schema')
        goal, confidence, reason = obj['goal'], obj['confidence'], obj['reason']
        if not isinstance(goal, str) or goal not in self.allowed_goals:
            raise ValueError('goal not authorized')
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not self.min_confidence <= confidence <= 1:
            raise ValueError('confidence below threshold')
        if not isinstance(reason, str) or len(reason) > 500:
            raise ValueError('invalid reason')
        return GoalProposal(goal, float(confidence), reason)
