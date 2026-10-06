from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Any
from atlas.security import Permission, PolicyEngine, RiskLevel
@dataclass(frozen=True)
class ToolManifest:
    name:str;description:str;permission:Permission;risk:RiskLevel=RiskLevel.LOW;side_effects:bool=False;timeout_seconds:float=30.0;schema:dict[str,Any]|None=None
@dataclass(frozen=True)
class ToolResult:
    success:bool;output:str;duration_ms:float=0.0
class ToolRegistry:
    def __init__(self,policy:PolicyEngine):self.policy=policy;self._tools={}
    def register(self,manifest,handler):self._tools[manifest.name]=(manifest,handler)
    def execute(self,name,*,confirmed=False,**kwargs):
        started=perf_counter()
        if name not in self._tools:return ToolResult(False,f'Unknown tool: {name}')
        manifest,handler=self._tools[name];decision=self.policy.evaluate(manifest.permission,manifest.risk)
        if not decision.allowed:return ToolResult(False,decision.reason)
        if decision.requires_confirmation and not confirmed:return ToolResult(False,'explicit confirmation required')
        try:r=handler(**kwargs);return ToolResult(r.success,r.output,round((perf_counter()-started)*1000,3))
        except Exception as exc:return ToolResult(False,f'tool failed: {exc}',round((perf_counter()-started)*1000,3))
    def manifests(self):return tuple(v[0] for v in self._tools.values())
