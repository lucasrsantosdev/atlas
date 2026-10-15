from types import SimpleNamespace

import pytest

from app.context.manager import build_context
from app.context.session_compaction import build_session_summary
from app.db.database import init_db
from app.models.conversation_repository import create_conversation
from app.models.message_repository import create_message
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_summary_preserves_explicit_constraints_and_source_references():
    messages = [
        SimpleNamespace(
            id=1,
            role="user",
            content="Decidimos não alterar a API pública; manter compatibilidade.",
        ),
        SimpleNamespace(
            id=2,
            role="assistant",
            content="Implementei a primeira parte da tarefa.",
        ),
        SimpleNamespace(
            id=3,
            role="tool",
            content="pytest falhou: conflito de caminho.",
        ),
    ]

    summary = build_session_summary(
        messages,
        "Retomar implementação do projeto",
        {"id": 7, "status": "executing", "plan": {"step": "test"}},
    )

    assert summary["schema_version"] == 1
    assert summary["objective"] == "Retomar implementação do projeto"
    assert summary["task_state"]["id"] == 7
    assert "não alterar a API pública" in summary["constraints"][0]["content"]
    assert summary["constraints"][0]["source_ref"] == "message:1"
    assert summary["observations"][0]["source_ref"] == "message:3"
    assert summary["open_issues"][0]["source_ref"] == "message:3"
    assert summary["source_refs"] == ["message:1", "message:2", "message:3"]
    assert any("original messages remain canonical" in item.lower() for item in summary["limitations"])


def test_context_compacts_older_messages_but_keeps_recent_history_and_current_request():
    model = create_model("Test", "ollama", "test:model")
    conversation = create_conversation("R3 compaction", model.id)

    for index in range(25):
        content = (
            "Requisito: não alterar a API pública; preservar compatibilidade."
            if index == 0
            else f"historical message {index}"
        )
        create_message(conversation.id, "user", content)
        create_message(conversation.id, "assistant", f"acknowledged {index}")
    create_message(conversation.id, "user", "Retome a tarefa")

    context = build_context(conversation.id)
    summaries = [
        item["content"]
        for item in context
        if item["role"] == "system" and "Mosaic derived session summary" in item["content"]
    ]

    assert len(summaries) == 1
    assert '"schema_version": 1' in summaries[0]
    assert "não alterar a API pública" in summaries[0]
    assert "message:" in summaries[0]
    assert any(item["content"] == "acknowledged 24" for item in context)
    assert context[-1] == {"role": "user", "content": "Retome a tarefa"}


def test_context_does_not_add_summary_when_history_fits_recent_window():
    model = create_model("Test", "ollama", "test:model")
    conversation = create_conversation("No compaction needed", model.id)
    create_message(conversation.id, "user", "Primeira mensagem")
    create_message(conversation.id, "user", "Mensagem atual")

    context = build_context(conversation.id)

    assert not any(
        item["role"] == "system" and "Mosaic derived session summary" in item["content"]
        for item in context
    )
