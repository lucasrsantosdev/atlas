import pytest

from app.services.agent_decision import parse_agent_decision


def test_parse_final_decision():
    assert parse_agent_decision('{"type":"final","content":"Concluído."}') == {
        "type": "final", "content": "Concluído."
    }


def test_parse_json_fenced_final_decision():
    assert parse_agent_decision('```json\n{"type":"final","content":"OK"}\n```') == {
        "type": "final", "content": "OK"
    }


def test_reject_invalid_json_and_unknown_decision_fields():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_agent_decision("resposta sem JSON")
    with pytest.raises(ValueError, match="unsupported fields"):
        parse_agent_decision('{"type":"final","content":"OK","reasoning":"private"}')


def test_reject_empty_final_response():
    with pytest.raises(ValueError, match="non-empty"):
        parse_agent_decision('{"type":"final","content":"  "}')


def test_tool_call_requires_registered_tool_and_valid_schema():
    with pytest.raises(ValueError, match="Unknown tool"):
        parse_agent_decision('{"type":"tool_call","tool":"made_up","arguments":{}}')
    with pytest.raises(ValueError, match="Missing required"):
        parse_agent_decision('{"type":"tool_call","tool":"calculator","arguments":{}}')


def test_tool_call_rejects_unknown_fields():
    with pytest.raises(ValueError, match="unsupported fields"):
        parse_agent_decision('{"type":"tool_call","tool":"calculator","arguments":{"expression":"1+1"},"extra":true}')
