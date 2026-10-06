from __future__ import annotations
import json
from dataclasses import dataclass,field
from datetime import datetime,timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4
@dataclass
class Trace:
 trace_id:str=field(default_factory=lambda:str(uuid4()));started_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat());events:list[dict[str,object]]=field(default_factory=list)
 def event(self,name,**data):self.events.append({'name':name,'at':datetime.now(timezone.utc).isoformat(),**data})
 def metrics(self):
  d=[float(e['duration_ms']) for e in self.events if e.get('duration_ms') is not None];return {'trace_id':self.trace_id,'events':len(self.events),'duration_ms':round(sum(d),3),'errors':sum(bool(e.get('error')) for e in self.events),'tool_calls':sum(e['name'].startswith('tool.') for e in self.events)}
 def persist(self,path):Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).open('a',encoding='utf8').write(json.dumps({'trace_id':self.trace_id,'started_at':self.started_at,'events':self.events},ensure_ascii=False)+'\n')
class Span:
 def __init__(self,trace,name,**attrs):self.trace,self.name,self.attrs=trace,name,attrs
 def __enter__(self):self.start=perf_counter();return self
 def __exit__(self,exc_type,exc,*_):self.trace.event(self.name,duration_ms=round((perf_counter()-self.start)*1000,3),error=str(exc) if exc else None,**self.attrs)
