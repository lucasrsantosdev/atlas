"""Validated sensor samples and bounded in-memory telemetry history."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Protocol
import math
import time

@dataclass(frozen=True)
class SensorSample:
    sensor: str
    value: float
    unit: str
    timestamp: float

    def __post_init__(self):
        if not self.sensor or not self.unit or not math.isfinite(self.value) or not math.isfinite(self.timestamp):
            raise ValueError("invalid sensor sample")

class Sensor(Protocol):
    def read(self) -> SensorSample: ...

class SensorHub:
    def __init__(self, capacity: int = 100):
        if capacity < 1: raise ValueError("capacity must be positive")
        self.history = deque(maxlen=capacity)
        self.latest: dict[str,SensorSample] = {}

    def publish(self, sample: SensorSample):
        previous = self.latest.get(sample.sensor)
        if previous and sample.timestamp < previous.timestamp: raise ValueError("stale sensor sample")
        self.latest[sample.sensor] = sample
        self.history.append(sample)

    def snapshot(self) -> dict[str,SensorSample]: return dict(self.latest)


    def fresh_snapshot(self, *, now: float, max_age: float) -> dict[str, SensorSample]:
        if not math.isfinite(now) or not math.isfinite(max_age) or max_age < 0:
            raise ValueError("invalid freshness settings")
        return {name: sample for name, sample in self.latest.items()
                if 0 <= now - sample.timestamp <= max_age}
