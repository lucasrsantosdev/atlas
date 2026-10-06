from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from atlas.knowledge import KnowledgeIndex
from atlas.memory import MemoryService
from atlas.mosaic import MosaicRequest,MosaicService
from atlas.models.router import ModelRouter
from atlas.models.runtime import ModelRequest
from atlas.observability import Span,Trace
class AgentState(str,Enum):UNDERSTAND='understand';RETRIEVE='retrieve';PLAN='plan';EXECUTE='execute';EVALUATE='evaluate';REPLAN='replan';RESPOND='respond';FAIL='fail'
@dataclass(frozen=True)
class AgentBudget:max_steps:int=10;max_replans:int=2;max_tool_calls:int=20
@dataclass(frozen=True)
class AgentResponse:response:str;trace:Trace;citations:tuple[str,...]=()
class AgentLoop:
 def __init__(self,router:ModelRouter,mosaic=None,memory=None,knowledge=None,budget=None):self.router=router;self.mosaic=mosaic or MosaicService();self.memory=memory;self.knowledge=knowledge;self.budget=budget or AgentBudget()
 def run(self,user_input):
  trace=Trace();state=AgentState.UNDERSTAND;steps=0;replans=0;contexts=[];citations=[]
  with Span(trace,state.value):analysis=self.mosaic.analyze(MosaicRequest(user_input));steps+=1
  state=AgentState.PLAN
  with Span(trace,state.value):plan=self.mosaic.plan(MosaicRequest(user_input));steps+=1
  state=AgentState.RETRIEVE
  if plan.needs_memory and self.memory:
   with Span(trace,'memory.retrieve'):
    memories=self.memory.recall_text(user_input,limit=5);contexts.extend(f'[memory:{m.id}] {m.content}' for m in memories)
  if plan.needs_knowledge and self.knowledge:
   with Span(trace,'knowledge.retrieve'):
    ctx,hits=self.knowledge.build_context(user_input,5)
    if ctx:contexts.append(ctx)
    citations.extend(h.citation for h in hits)
  steps+=1;role='code' if any(c.value=='code' for c in analysis.required_capabilities) and 'code' in self.router.available_roles() else 'primary'
  prompt=user_input if not contexts else 'Ground your answer only where context supports it. Cite sources when used.\n\n'+'\n\n'.join(contexts)+'\n\nUser request: '+user_input
  attempts=0
  while steps<min(plan.max_steps,self.budget.max_steps):
   state=AgentState.EXECUTE;attempts+=1;steps+=1
   try:
    caps=frozenset(c.value for c in analysis.required_capabilities)
    with Span(trace,'model.generate',role=role,attempt=attempts):result=self.router.generate_request(ModelRequest(prompt,caps or frozenset({'reasoning'}),preferred_role=role))
    state=AgentState.EVALUATE;trace.event('evaluate',success=bool(result.response.strip()),attempt=attempts)
    if result.response.strip():trace.event('respond',steps=steps,replans=replans);return AgentResponse(result.response,trace,tuple(dict.fromkeys(citations)))
   except Exception as exc:
    trace.event('evaluate',success=False,attempt=attempts,error=str(exc))
    if replans>=min(plan.max_retries,self.budget.max_replans):trace.event('fail',reason=str(exc));raise
    state=AgentState.REPLAN;replans+=1;trace.event('replan',number=replans);prompt+='\nPrevious attempt failed. Replan and answer robustly.'
  raise RuntimeError('agent budget exhausted')
