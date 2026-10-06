from __future__ import annotations
import re
from atlas.mosaic.models import CapabilityType, IntentType, MosaicRequest, MosaicResult
from atlas.mosaic.planning import ExecutionPlan, PlanRisk, PlanStep

class MosaicService:
    """Deterministic offline cognitive front-end with stable contracts."""
    def analyze(self, request: MosaicRequest) -> MosaicResult:
        text=request.user_input.strip(); low=text.casefold()
        if not text: raise ValueError('user_input não pode estar vazio')
        memory=any(x in low for x in ('lembre','memorize','recorde','remember'))
        retrieval=any(x in low for x in ('qual','quais','procure','busque','find','what','documento','conhecimento'))
        command=bool(re.match(r'^(crie|faça|execute|rode|abra|salve|gere|create|run|write)\b',low))
        question=text.endswith('?')
        intent=IntentType.MEMORY_REQUEST if memory else IntentType.COMMAND if command else IntentType.QUESTION if question else IntentType.RETRIEVAL if retrieval else IntentType.CONVERSATION
        code=any(x in low for x in ('código','python','java','git','teste','api','code','repository','repositório'))
        caps=(CapabilityType.CODE,CapabilityType.REASONING) if code else (CapabilityType.REASONING,) if question or command else (CapabilityType.FAST,)
        domain='software_engineering' if code else 'general'
        entities=tuple(dict.fromkeys(re.findall(r'\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\w.-]{2,}\b',text)))
        return MosaicResult(intent,domain,command,intent in {IntentType.QUESTION,IntentType.RETRIEVAL},entities,caps)

    def plan(self, request: MosaicRequest) -> ExecutionPlan:
        a=self.analyze(request); low=request.user_input.casefold()
        write=any(x in low for x in ('salve','escreva','delete','apague','commit','push','write'))
        capabilities=tuple(c.value for c in a.required_capabilities)
        steps=[]
        needs_context=a.requires_context
        if needs_context: steps += [PlanStep('retrieve','memory.read','Retrieve relevant memories'), PlanStep('retrieve','knowledge.read','Retrieve relevant knowledge')]
        if 'git' in low: steps.append(PlanStep('tool','git.read' if not write else 'git.write','Use Git capability'))
        steps.append(PlanStep('model','reasoning','Generate grounded response'))
        risk=PlanRisk.HIGH if write else PlanRisk.LOW
        complexity='high' if len(request.user_input)>500 or len(steps)>3 else 'medium' if len(steps)>1 else 'low'
        return ExecutionPlan(request.user_input,complexity,risk,needs_context,needs_context,capabilities,tuple(steps))
