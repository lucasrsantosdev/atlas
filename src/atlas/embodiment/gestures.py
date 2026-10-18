"""Explicit allowlisted gestures mapped to bounded simulated joint positions."""
from atlas.robotics.motion import MotionStep

GESTURES={
    "neutral":(MotionStep("head",90.0),),
    "nod":(MotionStep("head",105.0),MotionStep("head",90.0)),
    "look_left":(MotionStep("head",75.0),),
    "look_right":(MotionStep("head",105.0),),
}

def gesture_steps(name:str):
    if name not in GESTURES: raise ValueError("gesture is not allowlisted")
    return GESTURES[name]


from dataclasses import dataclass

@dataclass(frozen=True)
class GestureRequest:
    name: str
    priority: int = 0

class GestureScheduler:
    def __init__(self):
        self.active: GestureRequest | None = None

    def schedule(self, request: GestureRequest):
        gesture_steps(request.name)
        if self.active is not None and request.priority < self.active.priority:
            return False
        self.active = request
        return True

    def cancel(self):
        self.active = None
