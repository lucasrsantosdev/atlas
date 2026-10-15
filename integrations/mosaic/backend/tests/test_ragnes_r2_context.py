import pytest

from app.context.manager import build_context
from app.db.database import init_db
from app.models.conversation_repository import create_conversation
from app.models.message_repository import create_message
from app.models.project_repository import create_project
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_context_adds_ranked_lexical_evidence_with_source(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "backend").mkdir(parents=True)
    (workspace / "backend" / "harness.py").write_text(
        "def run():\n    # aprovação de ferramentas acontece antes da execução\n    pass\n",
        encoding="utf-8",
    )
    (workspace / "notes.txt").write_text("receita de bolo e jardinagem", encoding="utf-8")
    project = create_project("Test project", str(workspace))
    model = create_model("Local Model", "ollama", "local:test")
    conversation = create_conversation("Lexical context", model.id, project_id=project.id)
    create_message(conversation.id, "user", "Encontre aprovação de ferramentas")

    context = build_context(conversation.id)

    evidence = [item["content"] for item in context if "RAGNES lexical search evidence" in item["content"]]
    assert len(evidence) == 1
    assert "backend/harness.py" in evidence[0]
    assert "Lines 1-3" in evidence[0]
    assert "aprovação de ferramentas" in evidence[0]
    assert "untrusted data" in evidence[0]


def test_context_prefers_explicit_file_selection_over_lexical_search(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "selected.txt").write_text("selected source", encoding="utf-8")
    (workspace / "other.txt").write_text("other matching source", encoding="utf-8")
    project = create_project("Test project", str(workspace))
    model = create_model("Local Model", "ollama", "local:test")
    conversation = create_conversation("Explicit selection", model.id, project_id=project.id)
    create_message(conversation.id, "user", "Leia selected.txt")

    context = build_context(conversation.id)

    assert any("RAGNES selected artifact evidence" in item["content"] for item in context)
    assert not any("RAGNES lexical search evidence" in item["content"] for item in context)
