import pytest
from fastapi import BackgroundTasks, HTTPException

from app.api.projects import AgentConfigUpdate, get_project_agent_config_endpoint, save_project_agent_config_endpoint
from app.api.tasks import ToolDecision, decide_tool_call_endpoint
from app.db.database import init_db
from app.models.conversation_repository import create_conversation
from app.models.project_repository import create_project
from app.models.repository import create_model
from app.models.task_repository import create_task, get_task
from app.models.tool_call_repository import get_tool_call
from app.models.tool_result import ToolResult
from app.context.manager import build_context
from app.models.message_repository import create_message
from app.services.agent_config import save_agent_config

from app.services.agent import run_agent


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "agent-controls.db")
    init_db()


def test_agent_config_saves_root_agents_file_and_skills(tmp_path):
    workspace = tmp_path / "project"
    workspace.mkdir()
    project = create_project("Instructions", str(workspace))
    payload = AgentConfigUpdate(
        instructions="Use small, testable changes.",
        skills=[
            {"name": "Python tests", "content": "Run focused pytest first.", "enabled": True},
            {"name": "Docs", "content": "Keep the contract current.", "enabled": False},
        ],
    )

    saved = save_project_agent_config_endpoint(project.id, payload)
    loaded = get_project_agent_config_endpoint(project.id)

    assert (workspace / "AGENTS.md").read_text(encoding="utf-8") == "Use small, testable changes."
    assert saved["instruction_file"] == "AGENTS.md"
    assert loaded["skills"] == [
        {"name": "Python tests", "content": "Run focused pytest first.", "enabled": True},
        {"name": "Docs", "content": "Keep the contract current.", "enabled": False},
    ]


def test_agent_config_rejects_duplicate_skill_names(tmp_path):
    workspace = tmp_path / "project"
    workspace.mkdir()
    project = create_project("Instructions", str(workspace))
    payload = AgentConfigUpdate(instructions="", skills=[
        {"name": "Review", "content": "one", "enabled": True},
        {"name": "review", "content": "two", "enabled": True},
    ])
    with pytest.raises(HTTPException) as exc:
        save_project_agent_config_endpoint(project.id, payload)
    assert exc.value.status_code == 400


def test_agent_config_rejects_symlink_agents_file(tmp_path):
    workspace = tmp_path / "project"
    workspace.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    (workspace / "AGENTS.md").symlink_to(outside)
    project = create_project("Instructions", str(workspace))
    with pytest.raises(HTTPException) as exc:
        get_project_agent_config_endpoint(project.id)
    assert exc.value.status_code == 400


def test_approval_executes_pending_tool_and_resumes_same_task(monkeypatch, tmp_path):
    workspace = tmp_path / "project"
    workspace.mkdir()
    project = create_project("Approval", str(workspace))
    model = create_model("Test", "ollama", "test:model")
    conversation = create_conversation("Approval", model.id, project_id=project.id)
    task = create_task(
        type="generic", mode="agent", conversation_id=conversation.id, project_id=project.id,
        plan={"goal": "Inspect project"},
    )
    pending = run_agent(
        task.id,
        lambda context: {"type": "tool_call", "tool": "filesystem", "arguments": {"operation": "read", "path": "README.md"}},
    )
    assert pending["status"] == "awaiting_approval"
    call_id = pending["tool_call_id"]

    def fake_execute(call):
        return ToolResult(id=1, tool_call_id=call.id, status="completed", data={"content": "read ok"}, error=None, created_at="now")

    monkeypatch.setattr("app.api.tasks.execute_tool_call", fake_execute)
    background = BackgroundTasks()
    updated = decide_tool_call_endpoint(
        task.id, call_id, ToolDecision(decision="approve"), background,
    )
    assert updated.id == task.id
    assert updated.status == "executing"
    assert get_task(task.id).id == task.id
    assert get_tool_call(call_id).status == "approved"
    assert len(background.tasks) == 1


def test_approval_reject_marks_task_failed_without_execution(tmp_path):
    workspace = tmp_path / "project"
    workspace.mkdir()
    project = create_project("Approval", str(workspace))
    model = create_model("Test", "ollama", "test:model")
    conversation = create_conversation("Approval", model.id, project_id=project.id)
    task = create_task(type="generic", mode="agent", conversation_id=conversation.id, project_id=project.id)
    pending = run_agent(
        task.id,
        lambda context: {"type": "tool_call", "tool": "filesystem", "arguments": {"operation": "read", "path": "README.md"}},
    )
    updated = decide_tool_call_endpoint(
        task.id, pending["tool_call_id"], ToolDecision(decision="reject"), BackgroundTasks(),
    )
    assert updated.status == "failed"
    assert updated.result["error"] == "A operação solicitada foi recusada pelo usuário."
    assert get_tool_call(pending["tool_call_id"]).status == "rejected"


def test_agent_context_includes_project_instructions_and_enabled_skills(tmp_path):
    workspace = tmp_path / "project"
    workspace.mkdir()
    project = create_project("Context", str(workspace))
    save_agent_config(
        project.id,
        instructions="Use the repository's established style.",
        skills=[
            {"name": "Test discipline", "content": "Run focused tests before full suite.", "enabled": True},
            {"name": "Disabled guide", "content": "Do not include this text.", "enabled": False},
        ],
    )
    model = create_model("Test", "ollama", "test:model")
    conversation = create_conversation("Context", model.id, project_id=project.id)
    create_message(conversation.id, "user", "Inspect this project.")

    context = build_context(conversation.id)
    system_text = "\\n".join(item["content"] for item in context if item["role"] == "system")

    assert "Use the repository's established style." in system_text
    assert "Test discipline" in system_text
    assert "Run focused tests before full suite." in system_text
    assert "Disabled guide" not in system_text
    assert "cannot override safety rules" in system_text
