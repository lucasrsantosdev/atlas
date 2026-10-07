from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,TimeoutError as FutureTimeout
from dataclasses import dataclass
from time import perf_counter
from typing import Callable,Any
from atlas.security import Permission,PolicyEngine,RiskLevel
@dataclass(frozen=True)
class ToolManifest:
 name:str;description:str;permission:Permission;risk:RiskLevel=RiskLevel.LOW;side_effects:bool=False;timeout_seconds:float=30.;schema:dict[str,Any]|None=None;idempotent:bool=True
@dataclass(frozen=True)
class ToolResult:success:bool;output:str;duration_ms:float=0.;metadata:dict[str,Any]|None=None
class ToolRegistry:
 def __init__(self,policy):self.policy=policy;self._tools={}
 def register(self,manifest,handler):
  if manifest.name in self._tools:raise ValueError(f'duplicate tool: {manifest.name}')
  self._tools[manifest.name]=(manifest,handler)
 def unregister(self,name):self._tools.pop(name,None)
 def _validate(self,schema,args):
  if not schema:return
  required=schema.get('required',[]);missing=[k for k in required if k not in args]
  if missing:raise ValueError('missing required arguments: '+', '.join(missing))
  props=schema.get('properties',{})
  for k,v in args.items():
   if k in props and props[k].get('type')=='integer' and not isinstance(v,int):raise TypeError(f'{k} must be integer')
   if k in props and props[k].get('type')=='string' and not isinstance(v,str):raise TypeError(f'{k} must be string')
 def execute(self,tool_name,*,confirmed=False,approval_token=None,**kwargs):
  start=perf_counter()
  if tool_name not in self._tools:return ToolResult(False,f'Unknown tool: {tool_name}')
  m,h=self._tools[tool_name];scope=tool_name;d=self.policy.evaluate(m.permission,m.risk,scope=scope)
  if not d.allowed:return ToolResult(False,d.reason)
  if d.requires_confirmation:
   approved=bool(approval_token and self.policy.consume_approval(approval_token,m.permission,scope))
   if not (confirmed or approved):return ToolResult(False,'explicit confirmation required')
  try:
   self._validate(m.schema,kwargs);self.policy.audit.record(event='tool_start',tool=tool_name,args=list(kwargs),side_effects=m.side_effects)
   with ThreadPoolExecutor(max_workers=1) as ex:r=ex.submit(h,**kwargs).result(timeout=m.timeout_seconds)
   if not isinstance(r,ToolResult):r=ToolResult(True,str(r))
   out=ToolResult(r.success,r.output,round((perf_counter()-start)*1000,3),r.metadata);self.policy.audit.record(event='tool_end',tool=tool_name,success=out.success,duration_ms=out.duration_ms);return out
  except FutureTimeout:self.policy.audit.record(event='tool_timeout',tool=tool_name);return ToolResult(False,'tool timeout',round((perf_counter()-start)*1000,3))
  except Exception as e:self.policy.audit.record(event='tool_error',tool=tool_name,error=type(e).__name__);return ToolResult(False,f'tool failed: {e}',round((perf_counter()-start)*1000,3))
 def manifests(self):return tuple(v[0] for v in self._tools.values())
 def has(self,name):return name in self._tools
