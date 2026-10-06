from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4
@dataclass
class Trace:
    trace_id:str=field(default_factory=lambda:str(uuid4()));started_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat());events:list[dict[str,object]]=field(default_factory=list)
    def event(self,name:str,**data:object)->None:self.events.append({'name':name,'at':datetime.now(timezone.utc).isoformat(),**data})
    def metrics(self)->dict[str,object]:
        durations=[float(e['duration_ms']) for e in self.events if 'duration_ms' in e]
        return {'trace_id':self.trace_id,'events':len(self.events),'duration_ms':round(sum(durations),3),'errors':sum(1 for e in self.events if e.get('error'))}
class Span:
    def __init__(self,trace:Trace,name:str,**attrs):self.trace,self.name,self.attrs=trace,name,attrs
    def __enter__(self):self.start=perf_counter();return self
    def __exit__(self,exc_type,exc,*_):self.trace.event(self.name,duration_ms=round((perf_counter()-self.start)*1000,3),error=str(exc) if exc else None,**self.attrs)
