"""Logical safety guards for simulation; NOT a physical safety controller."""
from __future__ import annotations
import math
import time

class RoboticsSafety:
    def __init__(self, watchdog_seconds: float = 5.0, clock=None):
        if not math.isfinite(watchdog_seconds) or watchdog_seconds <= 0: raise ValueError("invalid watchdog")
        self.clock = clock or time.monotonic
        self.watchdog_seconds = watchdog_seconds
        self.last_seen = self.clock()
        self.latched = False

    def heartbeat(self):
        if self.latched: raise PermissionError("stop latched")
        self.last_seen = self.clock()

    def check(self):
        if self.clock() - self.last_seen > self.watchdog_seconds: self.latched = True
        if self.latched: raise PermissionError("robot is stopped")

    def stop(self): self.latched = True

    def reset(self, *, local_operator_confirmed: bool = False):
        if not local_operator_confirmed: raise PermissionError("local operator confirmation required")
        self.latched = False
        self.last_seen = self.clock()


    def allowed(self) -> bool:
        try:
            self.check()
        except PermissionError:
            return False
        return True

    def fail(self, reason: str = "fault"):
        self.latched = True
        self.reason = reason
