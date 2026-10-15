import pytest

from app.db.database import init_db
from app.models.conversation_repository import create_conversation
from app.models.repository import create_model
from app.models.task_repository import create_task, get_task, update_task
from app.models.tool_call_repository import get_tool_call
from app.models.tool_result_repository import list_tool_results
from app.services.agent import run_agent

@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()

def _conversation():
    model = create_model("Test", "ollama", "test:model")
    return create_conversation("Agent", model.id)

def _task():
    conversation = _conversation()
    return create_task(type="generic", mode="agent", conversation_id=conversation.id)

def test_agent_runs_tool_then_returns_final():
    task = _task()
    decisions = iter([
        {"type": "tool_call", "tool": "calculator", "arguments": {"expression": "2 + 3"}},
        {"type": "final", "content": "O resultado é 5."},
    ])
    result = run_agent(task.id, lambda context: next(decisions))
    assert result["status"] == "completed"
    assert result["iterations"] == 2
    assert get_task(task.id).status == "completed"

def test_agent_passes_tool_observation_to_next_decision():
    task = _task()
    observed = []
    def decide(context):
        observed.append(list(context))
        if len(observed) == 1:
            return {"type": "tool_call", "tool": "calculator", "arguments": {"expression": "7 * 6"}}
        assert any(message["role"] == "tool" and "42" in message["content"] for message in context)
        return {"type": "final", "content": "42"}
    result = run_agent(task.id, decide)
    assert result["status"] == "completed"
    assert len(observed) == 2

def test_agent_stops_for_approval_required_tool():
    task = _task()
    result = run_agent(task.id, lambda context: {"type": "tool_call", "tool": "filesystem", "arguments": {"operation": "read", "path": "README.md"}})
    assert result["status"] == "awaiting_approval"
    assert get_task(task.id).status == "awaiting_approval"
    call = get_tool_call(result["tool_call_id"])
    assert call.status == "pending"
    assert list_tool_results(call.id) == []

def test_agent_respects_iteration_limit():
    task = _task()
    result = run_agent(task.id, lambda context: {"type": "tool_call", "tool": "calculator", "arguments": {"expression": "1 + 1"}}, iteration_limit=2)
    assert result["status"] == "failed"
    assert result["iterations"] == 2
    assert get_task(task.id).status == "failed"

def test_agent_can_be_cancelled_before_tool_execution():
    task = _task()
    calls = 0
    def decide(context):
        nonlocal calls
        calls += 1
        update_task(task.id, status="cancelled")
        return {"type": "tool_call", "tool": "calculator", "arguments": {"expression": "1 + 1"}}
    result = run_agent(task.id, decide)
    assert result["status"] == "cancelled"
    assert calls == 1
