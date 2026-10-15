import pytest

from app.context.manager import build_context
from app.db.database import get_connection, init_db
from app.memory.manager import remember
from app.models.conversation_repository import create_conversation
from app.models.message_repository import create_message
from app.models.repository import create_model
from app.models.task_repository import create_task
from app.models.tool_call_repository import create_tool_call
from app.models.tool_result_repository import create_tool_result


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_context_includes_project_state_memory_before_history() -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO projects (name, workspace, state, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (
                "Mosaic",
                "/tmp/mosaic",
                '{"phase":"project"}',
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
            ),
        )
        connection.commit()

    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("Context test", model.id, project_id=1)

    remember(
        type="project_state",
        key="status",
        value="Memory implementation started",
        source="conversation",
        project_id=1,
    )
    create_message(conversation.id, "user", "Onde paramos?")

    context = build_context(conversation.id)

    assert context[0]["role"] == "system"
    assert "identidade" in context[0]["content"]
    assert any(
        item["role"] == "system"
        and "Mosaic project state:" in item["content"]
        and "{'phase': 'project'}" in item["content"]
        for item in context
    )
    assert any(
        item["role"] == "system"
        and "Mosaic memory" in item["content"]
        and "[project_state] status: Memory implementation started" in item["content"]
        for item in context
    )
    assert context[-1] == {"role": "user", "content": "Onde paramos?"}


def test_context_limits_history_and_keeps_current_user_message_last() -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("History limit", model.id)

    for index in range(25):
        create_message(conversation.id, "user", f"history-{index}")

    context = build_context(conversation.id)

    user_messages = [item["content"] for item in context if item["role"] == "user"]
    assert len(user_messages) == 21
    assert user_messages[:-1] == [f"history-{index}" for index in range(4, 24)]
    assert user_messages[-1] == "history-24"
    assert context[-1] == {"role": "user", "content": "history-24"}


def test_context_includes_current_task_and_tool_results() -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("Task context", model.id)

    create_task(
        type="analysis",
        mode="create",
        conversation_id=conversation.id,
        status="executing",
        plan={"step": "analyze"},
    )
    tool_call = create_tool_call(
        conversation_id=conversation.id,
        tool_name="calculator",
        arguments={"expression": "2 + 2"},
        status="completed",
    )
    create_tool_result(
        tool_call.id,
        status="completed",
        data={"value": 4},
    )
    create_message(conversation.id, "user", "Qual foi o resultado?")

    context = build_context(conversation.id)

    assert any(
        item["role"] == "system" and "Mosaic current task:" in item["content"]
        for item in context
    )
    assert any(
        item["role"] == "tool"
        and "calculator" in item["content"]
        and '"value": 4' in item["content"]
        for item in context
    )
    assert context[-1] == {"role": "user", "content": "Qual foi o resultado?"}



def test_context_always_includes_mosaic_identity_and_global_memory() -> None:
    model = create_model("Local Model", "ollama", "local:test")
    conversation = create_conversation("General conversation", model.id)
    remember(
        type="user_claim",
        key="alegacao",
        value="o Brasil foi descoberto em 2002",
        source="user",
    )
    create_message(conversation.id, "user", "Quando o Brasil foi descoberto?")

    context = build_context(conversation.id)

    assert context[0]["role"] == "system"
    assert "Sou o Mosaic, um assistente de inteligência artificial" in context[0]["content"]
    assert "O modelo de IA selecionado é responsável por gerar minhas respostas" in context[0]["content"]
    assert "não se apresente como um modelo genérico" in context[0]["content"]
    assert "não introduza alegações anteriores em respostas sem relação com elas" in context[0]["content"]
    assert "não mencione memórias do usuário, fatos históricos ou assuntos anteriores" in context[0]["content"]
    assert "Não invente datas de criação, lançamento ou disponibilidade do Mosaic" in context[0]["content"]
    assert "identidade nem a memória do sistema" in context[0]["content"]
    memory_messages = [item["content"] for item in context if item["role"] == "system" and "Mosaic memory" in item["content"]]
    assert len(memory_messages) == 1
    assert "[user_claim] alegacao: o Brasil foi descoberto em 2002" in memory_messages[0]


def test_identity_question_does_not_receive_unrelated_memories() -> None:
    model = create_model("Local Model", "ollama", "local:test")
    conversation = create_conversation("Identity question", model.id)
    remember(
        type="user_claim",
        key="alegacao",
        value="o Brasil foi descoberto em 2002",
        source="user",
    )
    create_message(conversation.id, "user", "Oi, quem é você?")

    context = build_context(conversation.id)

    assert "Sou o Mosaic, um assistente de inteligência artificial" in context[0]["content"]
    assert not any(
        item["role"] == "system" and "Mosaic memory" in item["content"]
        for item in context
    )
    assert not any("Brasil foi descoberto em 2002" in item["content"] for item in context)
    assert context[-1] == {"role": "user", "content": "Oi, quem é você?"}
