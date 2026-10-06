from __future__ import annotations
import time, json
from dataclasses import dataclass
from atlas.models.runtime import GenerationResult,ModelRequest,ModelRuntime,ModelRuntimeError
class ModelRouterError(RuntimeError):pass
@dataclass(frozen=True)
class ModelRoute:
    role:str;model_name:str;runtime:ModelRuntime;capabilities:frozenset[str]=frozenset({'reasoning'});priority:int=100;local:bool=True
@dataclass(frozen=True)
class RouterStatus: ready:bool;registered_routes:int;available_roles:tuple[str,...];detail:str
class ModelRouter:
    def __init__(self,retries:int=1,circuit_failures:int=3,circuit_cooldown:float=30):self._routes={};self.retries=retries;self.circuit_failures=circuit_failures;self.circuit_cooldown=circuit_cooldown;self._failures={};self._opened={}
    def register(self,*,role,model_name,runtime,capabilities=None,priority=100,local=True):
        role=role.strip().lower()
        if not role or not model_name.strip():raise ModelRouterError('role/model inválido')
        self._routes[role]=ModelRoute(role,model_name.strip(),runtime,frozenset(capabilities or {'reasoning'}),priority,local)
    def get_route(self,role):
        try:return self._routes[role.strip().lower()]
        except KeyError as e:raise ModelRouterError(f"Nenhum modelo registrado para a função '{role.strip().lower()}'.") from e
    def available_roles(self):return tuple(self._routes)
    def _candidates(self,req):
        now=time.monotonic();routes=list(self._routes.values())
        if req.preferred_role and req.preferred_role in self._routes:routes=[self._routes[req.preferred_role]]+[r for r in routes if r.role!=req.preferred_role]
        routes=[r for r in routes if req.capabilities<=r.capabilities and now>=self._opened.get(r.role,0)]
        if req.privacy=='local_only':routes=[r for r in routes if r.local]
        return sorted(routes,key=lambda r:r.priority)
    def generate_request(self,req:ModelRequest):
        errors=[]
        for route in self._candidates(req):
            if not route.runtime.health().available:continue
            for _ in range(self.retries+1):
                try:
                    out=route.runtime.generate(route.model_name,req.prompt,system_prompt=req.system_prompt);self._failures[route.role]=0
                    if req.structured:json.loads(out.response)
                    return out
                except Exception as e:
                    errors.append(f'{route.role}: {e}');self._failures[route.role]=self._failures.get(route.role,0)+1
                    if self._failures[route.role]>=self.circuit_failures:self._opened[route.role]=time.monotonic()+self.circuit_cooldown
        raise ModelRuntimeError('No healthy model route. '+'; '.join(errors))
    def generate(self,prompt,*,role='primary',system_prompt=None):
        r=self.get_route(role);return self.generate_request(ModelRequest(prompt,r.capabilities,system_prompt,role))
    def status(self):
        ok=tuple(r.role for r in self._routes.values() if r.runtime.health().available)
        return RouterStatus(bool(ok),len(self._routes),tuple(self._routes),'Model Router ativo.' if ok else 'Runtimes indisponíveis.')
