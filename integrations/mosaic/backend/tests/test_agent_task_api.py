import pytest
from fastapi import BackgroundTasks, HTTPException

from app.api.tasks import start_agent_task_endpoint, run_task_endpoint, TaskStart
from app.db.database import init_db
from app.models.conversation_repository import create_conversation
from app.models.message_repository import list_messages
from app.models.repository import create_model
from app.models.task_repository import create_task, get_task


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "agent-api.db")
    init_db()


def _conversation():
    model = create_model("Test", "ollama", "test:model")
    return create_conversation("Agent API", model.id)


def test_start_agent_persists_goal_and_schedules_one_task():
    conversation = _conversation()
    background = BackgroundTasks()

    task = start_agent_task_endpoint(
        TaskStart(conversation_id=conversation.id, goal="Analise o projeto"),
        background,
    )

    assert task.mode == "agent"
    assert task.status == "executing"
    assert task.plan == {"goal": "Analise o projeto"}
    assert task.conversation_id == conversation.id
    assert get_task(task.id).status == "executing"
    messages = list_messages(conversation.id)
    assert messages[-1].role == "user"
    assert messages[-1].content == "Analise o projeto"
    assert len(background.tasks) == 1


def test_start_agent_rejects_blank_goal():
    conversation = _conversation()
    with pytest.raises(HTTPException) as exc:
        start_agent_task_endpoint(
            TaskStart(conversation_id=conversation.id, goal="   "),
            BackgroundTasks(),
        )
    assert exc.value.status_code == 422


def test_run_endpoint_rejects_non_agent_task():
    conversation = _conversation()
    task = create_task(
        type="generic", mode="create", conversation_id=conversation.id
    )
    with pytest.raises(HTTPException) as exc:
        run_task_endpoint(task.id, BackgroundTasks())
    assert exc.value.status_code == 409
