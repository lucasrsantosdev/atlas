"""Validated bounded motion plans, no unbounded or implicit movement."""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class JointLimit:
    minimum: float = 30.0
    maximum: float = 150.0
    max_delta: float = 30.0

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.minimum,self.maximum,self.max_delta)) or self.minimum >= self.maximum or self.max_delta <= 0:
            raise ValueError("invalid joint limit")

@dataclass(frozen=True)
class MotionStep:
    joint: str
    angle: float

class MotionPlanner:
    def __init__(self, limits: dict[str, JointLimit]):
        if not limits: raise ValueError("at least one joint required")
        self.limits = dict(limits)

    def plan(self, steps: list[MotionStep], initial: dict[str, float]) -> tuple[MotionStep, ...]:
        if not steps: raise ValueError("empty motion plan")
        state = dict(initial)
        for step in steps:
            if step.joint not in self.limits: raise ValueError("unknown joint")
            limit = self.limits[step.joint]
            if isinstance(step.angle,bool) or not isinstance(step.angle,(int,float)) or not math.isfinite(step.angle): raise ValueError("invalid angle")
            if not limit.minimum <= step.angle <= limit.maximum: raise ValueError("joint angle outside bounds")
            previous = state.get(step.joint)
            if previous is None or not math.isfinite(previous) or abs(step.angle - previous) > limit.max_delta:
                raise ValueError("unsafe motion increment")
            state[step.joint] = step.angle
        return tuple(steps)


@dataclass(frozen=True)
class TimedMotionStep:
    joint: str
    angle: float
    at_seconds: float

def interpolate_motion(start: float, target: float, *, joint: str, limit: JointLimit,
                       max_velocity: float, max_acceleration: float, dt: float = 0.05) -> tuple[TimedMotionStep, ...]:
    """Trapezoidal/triangular velocity profile with bounded discrete increments."""
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
               for v in (start, target, max_velocity, max_acceleration, dt)):
        raise ValueError("invalid trajectory input")
    if not (limit.minimum <= start <= limit.maximum and limit.minimum <= target <= limit.maximum):
        raise ValueError("trajectory outside joint bounds")
    if max_velocity <= 0 or max_acceleration <= 0 or dt <= 0:
        raise ValueError("invalid trajectory parameters")
    distance = abs(target - start)
    if distance == 0:
        return (TimedMotionStep(joint, target, 0.0),)
    ramp = max_velocity * max_velocity / max_acceleration
    if distance <= ramp:
        t_acc = math.sqrt(distance / max_acceleration)
        total = 2 * t_acc
        v_peak = max_acceleration * t_acc
        cruise = 0.0
    else:
        t_acc = max_velocity / max_acceleration
        cruise = (distance - ramp) / max_velocity
        total = 2 * t_acc + cruise
        v_peak = max_velocity
    n = math.ceil(total / dt)
    if n > 10000:
        raise ValueError("trajectory exceeds sample limit")
    direction = 1 if target > start else -1
    result = []
    for i in range(1, n + 1):
        t = min(total, i * dt)
        if t <= t_acc:
            traveled = .5 * max_acceleration * t * t
        elif t <= t_acc + cruise:
            traveled = .5 * max_acceleration * t_acc * t_acc + v_peak * (t - t_acc)
        else:
            remaining = total - t
            traveled = distance - .5 * max_acceleration * remaining * remaining
        angle = target if i == n else start + direction * traveled
        if abs(angle - (result[-1].angle if result else start)) > limit.max_delta + 1e-8:
            raise ValueError("trajectory step exceeds joint delta limit")
        result.append(TimedMotionStep(joint, angle, t))
    return tuple(result)
