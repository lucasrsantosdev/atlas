"""Map affect to high-level intent, never to hardware commands."""
from atlas.robotics.cognition.behavior_planner import Intent
from .emotion import Affect
from .personality import Personality

class ExpressionPlanner:
    def plan(self, affect: Affect, personality: Personality | None = None) -> Intent:
        personality=personality or Personality()
        mapping={'happy':'express_happiness','sad':'acknowledge','concerned':'acknowledge','neutral':'neutral'}
        name=mapping.get(affect.label,'neutral')
        return Intent(name, min(1.,max(0.,affect.confidence*personality.expressiveness)))
