"""Context-aware intent -> safe, validated simulated joint trajectories.

No LLM is required. An external model may suggest an Intent, never raw servo commands.
The caller must authorize execution separately; planning has no side effects.
"""
from dataclasses import dataclass
import math
from atlas.robotics.motion import JointLimit, TimedMotionStep, interpolate_motion

@dataclass(frozen=True)
class Intent:
    name: str
    intensity: float = 0.5
    duration_seconds: float = 1.0
    def __post_init__(self):
        if not isinstance(self.name,str) or not self.name: raise ValueError("intent name required")
        if isinstance(self.intensity,bool) or not isinstance(self.intensity,(int,float)) or not math.isfinite(self.intensity) or not 0 <= self.intensity <= 1: raise ValueError("invalid intensity")
        if isinstance(self.duration_seconds,bool) or not isinstance(self.duration_seconds,(int,float)) or not math.isfinite(self.duration_seconds) or not 0 < self.duration_seconds <= 10: raise ValueError("invalid duration")

@dataclass(frozen=True)
class BehaviorPlan:
    intent: Intent
    action: str
    trajectory: tuple[TimedMotionStep,...]

class BehaviorPlanner:
    """Dynamic head targets based on intent, intensity and current position."""
    ALLOWED = frozenset({'acknowledge','look_left','look_right','neutral','express_happiness'})
    def __init__(self, *, limits: dict[str,JointLimit] | None = None):
        self.limits=limits or {'head':JointLimit()}
    def plan(self, intent: Intent, joints: dict[str,float], *, safety=None) -> BehaviorPlan:
        if intent.name not in self.ALLOWED: raise ValueError("intent not allowed")
        if safety is not None: safety.check()
        if 'head' not in joints or 'head' not in self.limits: raise ValueError("head joint required")
        start=joints['head']
        if isinstance(start,bool) or not isinstance(start,(float,int)) or not math.isfinite(start): raise ValueError("invalid initial joint")
        offsets={'acknowledge':12.,'look_left':-30.,'look_right':30.,'neutral':0.,'express_happiness':18.}
        target=90. if intent.name=='neutral' else start+offsets[intent.name]*intent.intensity
        lim=self.limits['head']
        target=max(lim.minimum,min(lim.maximum,target))
        # A duration is a requested timing preference, not an unsafe velocity override.
        velocity=min(35.,max(2.,abs(target-start)/intent.duration_seconds*1.5))
        trajectory=interpolate_motion(start,target,joint='head',limit=lim,max_velocity=velocity,max_acceleration=90.)
        return BehaviorPlan(intent,intent.name,trajectory)
