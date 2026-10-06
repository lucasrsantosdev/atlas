from __future__ import annotations
from dataclasses import dataclass
from atlas.knowledge import KnowledgeIndex
from atlas.memory import MemoryService
from atlas.mosaic import MosaicRequest, MosaicService
from atlas.models.router import ModelRouter
from atlas.observability import Span, Trace

@dataclass(frozen=True)
class AgentResponse:
    response:str; trace:Trace; citations:tuple[str,...]=()
class AgentLoop:
    """Bounded Understand→Retrieve→Plan→Execute→Observe→Evaluate loop."""
    def __init__(self,router:ModelRouter,mosaic:MosaicService|None=None,memory:MemoryService|None=None,knowledge:KnowledgeIndex|None=None):
        self.router=router;self.mosaic=mosaic or MosaicService();self.memory=memory;self.knowledge=knowledge
    def run(self,user_input:str)->AgentResponse:
        trace=Trace()
        with Span(trace,'understand'):analysis=self.mosaic.analyze(MosaicRequest(user_input))
        with Span(trace,'plan'):plan=self.mosaic.plan(MosaicRequest(user_input))
        contexts=[];citations=[]
        if plan.needs_memory and self.memory:
            with Span(trace,'memory.retrieve'):
                memories=self.memory.recall_text(user_input,limit=5);contexts.extend(f'[memory:{m.id}] {m.content}' for m in memories)
        if plan.needs_knowledge and self.knowledge:
            with Span(trace,'knowledge.retrieve'):
                ctx,hits=self.knowledge.build_context(user_input,5);contexts.append(ctx) if ctx else None;citations.extend(h.citation for h in hits)
        role='code' if any(c.value=='code' for c in analysis.required_capabilities) and 'code' in self.router.available_roles() else 'primary'
        trace.event('execution_plan',complexity=plan.complexity,risk=plan.risk.value,model_role=role,steps=len(plan.steps))
        prompt=user_input if not contexts else 'Ground your answer in this retrieved context. Do not invent missing facts.\n\n'+'\n\n'.join(contexts)+'\n\nUser request: '+user_input
        attempts=0
        while True:
            attempts+=1
            try:
                with Span(trace,'model.generate',role=role,attempt=attempts):result=self.router.generate(prompt,role=role)
                trace.event('evaluate',success=True,attempt=attempts);return AgentResponse(result.response,trace,tuple(dict.fromkeys(citations)))
            except Exception as exc:
                trace.event('evaluate',success=False,attempt=attempts,error=str(exc))
                if attempts>plan.max_retries:raise
