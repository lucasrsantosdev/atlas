from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4
@dataclass
class Trace:
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events: list[dict[str, object]] = field(default_factory=list)
    def event(self, name: str, **data: object) -> None: self.events.append({"name":name,"at":datetime.now(timezone.utc).isoformat(),**data})
class Span:
    def __init__(self, trace: Trace, name: str): self.trace,self.name=trace,name
    def __enter__(self): self.start=perf_counter(); return self
    def __exit__(self,*_): self.trace.event(self.name, duration_ms=round((perf_counter()-self.start)*1000,3))
