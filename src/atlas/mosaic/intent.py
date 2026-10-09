"""Deterministic intent classification for Mosaic v0.1."""
from __future__ import annotations
import re
import unicodedata
from atlas.mosaic.models import IntentType

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text).strip()

def classify_intent(text: str) -> IntentType:
    s = normalize(text)
    if not s:
        return IntentType.UNKNOWN
    if re.search(r"\b(nao guarde|nao memorize|nao lembre|esqueca|apague da memoria)\b", s):
        return IntentType.MEMORY_REQUEST
    if re.search(r"\b(lembre que|memorize|guarde na memoria|salve na memoria|o que voce lembra|voce se lembra)\b", s):
        return IntentType.MEMORY_REQUEST
    if re.search(r"^(procure|busque|pesquise|localize|encontre|consulte)\b", s) or re.search(r"\b(nos documentos|na biblioteca|na base de conhecimento)\b", s):
        return IntentType.RETRIEVAL
    if re.search(r"^(execute|rode|abra|inicie|reinicie|desligue|ligue|delete|exclua|remova|envie|instale)\b", s):
        return IntentType.COMMAND
    if re.search(r"^(crie|gere|escreva|desenvolva|implemente|monte|construa|refatore|corrija|elabore)\b", s):
        return IntentType.TASK
    if s.endswith('?') or re.search(r"^(o que|quem|qual|quais|como|por que|porque|quando|onde|quanto|explique|me explique)\b", s):
        return IntentType.QUESTION
    if re.fullmatch(r"(ola|oi|bom dia|boa tarde|boa noite|obrigad[oa]|valeu|tudo bem|e ai)[!. ]*", s):
        return IntentType.CONVERSATION
    return IntentType.CONVERSATION
