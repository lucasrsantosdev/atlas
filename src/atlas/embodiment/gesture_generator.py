"""Generate a context-dependent plan without growing a fixed gesture dictionary."""
from atlas.robotics.cognition.behavior_planner import BehaviorPlanner, BehaviorPlan
from .emotion import EmotionInterpreter
from .expression_planner import ExpressionPlanner
from .personality import Personality

class GestureGenerator:
    def __init__(self, planner: BehaviorPlanner | None = None):
        self.planner=planner or BehaviorPlanner()
        self.interpreter=EmotionInterpreter()
        self.expressions=ExpressionPlanner()
    def generate(self, text: str, joints: dict[str,float], *, personality: Personality | None = None, safety=None) -> BehaviorPlan:
        affect=self.interpreter.interpret(text)
        intent=self.expressions.plan(affect,personality)
        return self.planner.plan(intent,joints,safety=safety)
