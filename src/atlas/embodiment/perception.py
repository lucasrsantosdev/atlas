"""Opt-in perception events; no implicit camera access or recognition."""
from __future__ import annotations
from dataclasses import dataclass
import time

@dataclass(frozen=True)
class PerceptionEvent:
    kind:str
    detail:str
    timestamp:float

class PerceptionBuffer:
    def __init__(self,max_events=32):
        if max_events<1: raise ValueError("max_events must be positive")
        self.max_events=max_events;self.events=[]

    def add(self,kind,detail,*,timestamp=None):
        if not kind or not detail: raise ValueError("empty perception event")
        event=PerceptionEvent(kind,detail,time.monotonic() if timestamp is None else timestamp)
        self.events=(self.events+[event])[-self.max_events:]
        return event


    def recent(self, *, now: float, max_age: float, kind: str | None = None):
        import math
        if not math.isfinite(now) or not math.isfinite(max_age) or max_age < 0:
            raise ValueError("invalid event age")
        return tuple(event for event in self.events
                     if 0 <= now - event.timestamp <= max_age
                     and (kind is None or event.kind == kind))
