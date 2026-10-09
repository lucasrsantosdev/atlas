"""Deterministic and safety-contract tests for Mosaic v0.1."""
import pytest
from atlas.mosaic.intent import classify_intent
from atlas.mosaic.entities import extract_entities
from atlas.mosaic.context import select_context
from atlas.mosaic.models import ContextItem, IntentType, MosaicRequest, CapabilityType
from atlas.mosaic.service import MosaicService

@pytest.mark.parametrize("text,expected", [
    ("Olá Atlas", IntentType.CONVERSATION),
    ("O que é inteligência artificial?", IntentType.QUESTION),
    ("Lembre que estudo Python", IntentType.MEMORY_REQUEST),
    ("Não memorize minha senha", IntentType.MEMORY_REQUEST),
    ("Procure o documento de arquitetura", IntentType.RETRIEVAL),
    ("Crie um código Python", IntentType.TASK),
    ("Execute o programa", IntentType.COMMAND),
    ("   ", IntentType.UNKNOWN),
])
def test_classify_intent(text, expected):
    assert classify_intent(text) == expected

def test_entity_extraction_deduplicates():
    assert extract_entities("Atlas usa Python e python") == ("Atlas", "Python")

def test_context_filters_and_orders():
    ctx = [ContextItem("documento sobre astronomia", "doc1", 0.0), ContextItem("Python para iniciantes", "doc2", 0.0)]
    result = select_context("Python", ctx)
    assert len(result) == 1 and result[0].source == "doc2"

def test_service_contract():
    result = MosaicService().analyze(MosaicRequest("Crie um código Python"))
    assert result.intent is IntentType.TASK
    assert result.is_task is True
    assert result.domain == "programming"
    assert result.required_capabilities == (CapabilityType.CODE,)
    assert result.memory_candidates == ()

def test_service_does_not_store_memory():
    result = MosaicService().analyze(MosaicRequest("Lembre que estudo Python"))
    assert result.intent is IntentType.MEMORY_REQUEST
    assert result.memory_candidates == ()
    assert result.is_task is False

def test_service_rejects_wrong_request_type():
    with pytest.raises(TypeError):
        MosaicService().analyze("oi")
