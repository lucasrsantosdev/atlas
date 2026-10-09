"""Task detection and capability routing hints (no execution)."""
from __future__ import annotations
from atlas.mosaic.intent import normalize
from atlas.mosaic.models import CapabilityType, IntentType

def is_task(intent: IntentType) -> bool:
    return intent in {IntentType.TASK, IntentType.COMMAND}

def classify_domain(text: str) -> str:
    s = normalize(text)
    for domain, terms in (
        ("programming", ("python", "codigo", "programa", "funcao", "script", "refatore", "bug")),
        ("robotics", ("robo", "esp32", "arduino", "sensor", "servo", "motor")),
        ("science", ("ciencia", "cientifico", "fisica", "quimica", "biologia")),
        ("education", ("escola", "aluno", "professor", "aula", "educacao", "ensinar")),
        ("atlas", ("atlas", "mosaic", "memoria", "arquitetura", "knowledge")),
    ):
        if any(term in s for term in terms):
            return domain
    return "general"

def required_capabilities(text: str, intent: IntentType, domain: str) -> tuple[CapabilityType, ...]:
    if domain == "programming":
        return (CapabilityType.CODE,)
    if domain == "robotics":
        return (CapabilityType.ENGINEERING,)
    if domain == "science":
        return (CapabilityType.SCIENCE,)
    if intent in (IntentType.TASK, IntentType.COMMAND):
        return (CapabilityType.REASONING,)
    return (CapabilityType.FAST,)
