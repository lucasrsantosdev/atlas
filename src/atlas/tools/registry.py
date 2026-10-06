from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,TimeoutError as FutureTimeout
from dataclasses import dataclass
from time import perf_counter
from typing import Callable,Any
from atlas.security import Permission,PolicyEngine,RiskLevel
@dataclass(frozen=True)
class ToolManifest:name:str;description:str;permission:Permission;risk:RiskLevel=RiskLevel.LOW;side_effects:bool=False;timeout_seconds:float=30.;schema:dict[str,Any]|None=None
@dataclass(frozen=True)
class ToolResult:success:bool;output:str;duration_ms:float=0.;metadata:dict[str,Any]|None=None
class ToolRegistry:
 def __init__(self,policy):self.policy=policy;self._tools={}
 def register(self,manifest,handler):self._tools[manifest.name]=(manifest,handler)
 def execute(self,name,*,confirmed=False,**kwargs):
  start=perf_counter()
  if name not in self._tools:return ToolResult(False,f'Unknown tool: {name}')
  m,h=self._tools[name];d=self.policy.evaluate(m.permission,m.risk)
  if not d.allowed:return ToolResult(False,d.reason)
  if d.requires_confirmation and not confirmed:return ToolResult(False,'explicit confirmation required')
  try:
   with ThreadPoolExecutor(max_workers=1) as ex:r=ex.submit(h,**kwargs).result(timeout=m.timeout_seconds)
   if not isinstance(r,ToolResult):r=ToolResult(True,str(r))
   return ToolResult(r.success,r.output,round((perf_counter()-start)*1000,3),r.metadata)
  except FutureTimeout:return ToolResult(False,'tool timeout',round((perf_counter()-start)*1000,3))
  except Exception as e:return ToolResult(False,f'tool failed: {e}',round((perf_counter()-start)*1000,3))
 def manifests(self):return tuple(v[0] for v in self._tools.values())
 def has(self,name):return name in self._tools
