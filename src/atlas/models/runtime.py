from __future__ import annotations
import json, urllib.error, urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator
class ModelRuntimeError(RuntimeError): pass
@dataclass(frozen=True)
class RuntimeHealth: available:bool; provider:str; detail:str
@dataclass(frozen=True)
class GenerationResult:
    model:str; response:str; provider:str='unknown'; input_tokens:int|None=None; output_tokens:int|None=None
@dataclass(frozen=True)
class ModelRequest:
    prompt:str; capabilities:frozenset[str]=frozenset({'reasoning'}); system_prompt:str|None=None; preferred_role:str|None=None; privacy:str='local_preferred'; timeout_seconds:float=60.0; structured:bool=False
class ModelRuntime(ABC):
    @property
    @abstractmethod
    def provider(self)->str: ...
    @abstractmethod
    def health(self)->RuntimeHealth: ...
    @abstractmethod
    def generate(self,model:str,prompt:str,*,system_prompt:str|None=None)->GenerationResult: ...
    def stream(self,model:str,prompt:str,*,system_prompt:str|None=None)->Iterator[str]:
        yield self.generate(model,prompt,system_prompt=system_prompt).response
class OllamaRuntime(ModelRuntime):
    def __init__(self,base_url='http://127.0.0.1:11434',timeout=60.0):self.base_url=base_url.rstrip('/');self.timeout=timeout
    @property
    def provider(self):return 'ollama'
    def _request(self,path,payload=None):
        data=None if payload is None else json.dumps(payload).encode();req=urllib.request.Request(f'{self.base_url}{path}',data=data,headers={'Content-Type':'application/json'},method='POST' if payload is not None else 'GET')
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r:return json.loads(r.read().decode())
        except (urllib.error.URLError,TimeoutError,json.JSONDecodeError) as e:raise ModelRuntimeError(f'Ollama indisponível: {e}') from e
    def health(self):
        try:self._request('/api/tags');return RuntimeHealth(True,self.provider,'Ollama disponível.')
        except ModelRuntimeError as e:return RuntimeHealth(False,self.provider,str(e))
    def generate(self,model,prompt,*,system_prompt=None):
        payload={'model':model,'prompt':prompt,'stream':False};
        if system_prompt:payload['system']=system_prompt
        d=self._request('/api/generate',payload);response=str(d.get('response','')).strip()
        if not response:raise ModelRuntimeError('Ollama retornou resposta vazia.')
        return GenerationResult(model,response,self.provider,d.get('prompt_eval_count'),d.get('eval_count'))
