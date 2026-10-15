import pytest

from app.context.manager import build_context
from app.db.database import get_connection, init_db
from app.models.conversation_repository import create_conversation
from app.models.message_repository import create_message
from app.models.project_repository import create_project
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def _conversation_for_workspace(workspace, user_message):
    project = create_project("Test project", str(workspace))
    model = create_model("Local Model", "ollama", "local:test")
    conversation = create_conversation("Artifact context", model.id, project_id=project.id)
    create_message(conversation.id, "user", user_message)
    return conversation


def test_context_reads_only_explicitly_named_workspace_artifact(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "src").mkdir()
    (workspace / "src" / "main.py").write_text(chr(10).join(["line one", "selected evidence", "line three"]), encoding="utf-8")
    (workspace / "other.py").write_text("must not be injected", encoding="utf-8")
    conversation = _conversation_for_workspace(workspace, "Analise src/main.py")

    context = build_context(conversation.id)

    evidence = [item["content"] for item in context if "RAGNES selected artifact evidence" in item["content"]]
    assert len(evidence) == 1
    assert "Source: src/main.py lines 1-3" in evidence[0]
    assert "selected evidence" in evidence[0]
    assert "must not be injected" not in str(context)
    assert context[-1] == {"role": "user", "content": "Analise src/main.py"}


def test_context_does_not_read_artifacts_without_explicit_path(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "main.py").write_text("secret file body", encoding="utf-8")
    conversation = _conversation_for_workspace(workspace, "Analise o código do projeto")

    context = build_context(conversation.id)

    assert not any("RAGNES selected artifact evidence" in item["content"] for item in context)
    assert "secret file body" not in str(context)


def test_context_ignores_paths_outside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside secret", encoding="utf-8")
    (workspace / "outside.txt").write_text("inside decoy secret", encoding="utf-8")
    conversation = _conversation_for_workspace(workspace, "Leia ../outside.txt")

    context = build_context(conversation.id)

    assert not any("RAGNES selected artifact evidence" in item["content"] for item in context)
    assert "outside secret" not in str(context)
    assert "inside decoy secret" not in str(context)


def test_context_bounds_number_of_explicit_artifacts(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for name in ("a.py", "b.py", "c.py", "d.py"):
        (workspace / name).write_text(f"content-{name}", encoding="utf-8")
    conversation = _conversation_for_workspace(
        workspace,
        "Leia a.py b.py c.py d.py e explique",
    )

    context = build_context(conversation.id)

    evidence = [item["content"] for item in context if "RAGNES selected artifact evidence" in item["content"]]
    assert len(evidence) <= 3
    assert "content-d.py" not in str(evidence)
