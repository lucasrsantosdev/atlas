"""Mosaic v0.1 analysis pipeline: interpretation only, never execution."""
from __future__ import annotations
from collections.abc import Iterable
from atlas.mosaic.context import select_context
from atlas.mosaic.entities import extract_entities
from atlas.mosaic.intent import classify_intent
from atlas.mosaic.models import ContextItem, IntentType, MosaicRequest, MosaicResult
from atlas.mosaic.task_classifier import classify_domain, is_task, required_capabilities

class MosaicService:
    """Analyze user requests without executing tools or persisting memory."""

    def __init__(self, available_context: Iterable[ContextItem] = ()) -> None:
        self._available_context = tuple(available_context)

    def analyze(self, request: MosaicRequest) -> MosaicResult:
        if not isinstance(request, MosaicRequest):
            raise TypeError("request must be a MosaicRequest")
        text = request.user_input
        if not isinstance(text, str):
            raise TypeError("user_input must be a string")
        intent = classify_intent(text)
        domain = classify_domain(text)
        requires_context = intent in {IntentType.QUESTION, IntentType.RETRIEVAL, IntentType.TASK}
        selected = select_context(text, self._available_context) if requires_context else ()
        return MosaicResult(
            intent=intent,
            domain=domain,
            is_task=is_task(intent),
            requires_context=requires_context,
            entities=extract_entities(text),
            required_capabilities=required_capabilities(text, intent, domain),
            context=selected,
            memory_candidates=(),
        )
