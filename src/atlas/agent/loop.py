from __future__ import annotations
from dataclasses import dataclass
from atlas.mosaic import MosaicRequest, MosaicService
from atlas.models.router import ModelRouter
from atlas.observability import Span, Trace
@dataclass(frozen=True)
class AgentResponse:
    response:str; trace:Trace
class AgentLoop:
    def __init__(self,router:ModelRouter,mosaic:MosaicService|None=None): self.router=router;self.mosaic=mosaic or MosaicService()
    def run(self,user_input:str)->AgentResponse:
        trace=Trace()
        with Span(trace,"mosaic"): analysis=self.mosaic.analyze(MosaicRequest(user_input))
        role="code" if any(c.value=="code" for c in analysis.required_capabilities) and "code" in self.router.available_roles() else "primary"
        trace.event("plan",intent=analysis.intent.value,domain=analysis.domain,model_role=role)
        with Span(trace,"model"): result=self.router.generate(user_input,role=role)
        return AgentResponse(result.response,trace)
