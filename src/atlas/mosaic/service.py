from __future__ import annotations
import re
from atlas.mosaic.models import CapabilityType, IntentType, MosaicRequest, MosaicResult
class MosaicService:
    """Classificador determinístico offline. Pode ser substituído/enriquecido por modelo sem mudar o contrato."""
    def analyze(self,request:MosaicRequest)->MosaicResult:
        text=request.user_input.strip(); low=text.casefold()
        if not text: raise ValueError("user_input não pode estar vazio")
        memory=any(x in low for x in ("lembre","memorize","recorde","remember"))
        retrieval=any(x in low for x in ("qual","quais","procure","busque","find","what"))
        command=bool(re.match(r"^(crie|faça|execute|rode|abra|salve|gere|create|run|write)\b",low))
        question=text.endswith("?")
        intent=IntentType.MEMORY_REQUEST if memory else IntentType.COMMAND if command else IntentType.QUESTION if question else IntentType.RETRIEVAL if retrieval else IntentType.CONVERSATION
        code=any(x in low for x in ("código","python","java","git","teste","api","code"))
        caps=(CapabilityType.CODE,CapabilityType.REASONING) if code else (CapabilityType.REASONING,) if question or command else (CapabilityType.FAST,)
        domain="software_engineering" if code else "general"
        entities=tuple(dict.fromkeys(re.findall(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\w.-]{2,}\b",text)))
        return MosaicResult(intent,domain,command,intent in {IntentType.QUESTION,IntentType.RETRIEVAL},entities,caps)
