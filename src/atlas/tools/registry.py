from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from atlas.security import Permission, PolicyEngine, RiskLevel
@dataclass(frozen=True)
class ToolManifest:
    name:str; description:str; permission:Permission; risk:RiskLevel=RiskLevel.LOW; side_effects:bool=False
@dataclass(frozen=True)
class ToolResult:
    success:bool; output:str
class ToolRegistry:
    def __init__(self,policy:PolicyEngine): self.policy=policy; self._tools:dict[str,tuple[ToolManifest,Callable[...,ToolResult]]]={}
    def register(self,manifest:ToolManifest,handler:Callable[...,ToolResult]): self._tools[manifest.name]=(manifest,handler)
    def execute(self,name:str,*,confirmed:bool=False,**kwargs)->ToolResult:
        if name not in self._tools:return ToolResult(False,f"Unknown tool: {name}")
        manifest,handler=self._tools[name]; decision=self.policy.evaluate(manifest.permission,manifest.risk)
        if not decision.allowed:return ToolResult(False,decision.reason)
        if decision.requires_confirmation and not confirmed:return ToolResult(False,"explicit confirmation required")
        try:return handler(**kwargs)
        except Exception as exc:return ToolResult(False,f"tool failed: {exc}")
    def manifests(self): return tuple(v[0] for v in self._tools.values())
