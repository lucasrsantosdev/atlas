import pytest
from fastapi.testclient import TestClient

from app.context.manager import build_context
from app.db.database import init_db
from app.main import app
from app.memory.manager import remember
from app.models.conversation_repository import create_conversation
from app.models.message_repository import create_message
from app.models.project_repository import create_project
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_context_proof_keeps_project_state_memory_and_history_isolated(
    client: TestClient,
    monkeypatch,
) -> None:
    guitar = create_project(
        name="Guitar Livre",
        workspace="/tmp/guitar-livre",
        state={"project": "guitar", "phase": "chart"},
    )
    tennis = create_project(
        name="Table Tennis Motion Lab",
        workspace="/tmp/tennis",
        state={"project": "tennis", "phase": "tracking"},
    )
    model = create_model("Local Model", "ollama", "local:test")

    guitar_conversation = client.post(
        "/conversations",
        json={"title": "Guitar context", "model_id": model.id, "project_id": guitar.id},
    ).json()
    tennis_conversation = client.post(
        "/conversations",
        json={"title": "Tennis context", "model_id": model.id, "project_id": tennis.id},
    ).json()

    remember(
        type="project_state",
        key="focus",
        value="gerar charts para guitarra",
        source="conversation",
        project_id=guitar.id,
    )
    remember(
        type="project_state",
        key="focus",
        value="rastrear movimento da raquete",
        source="conversation",
        project_id=tennis.id,
    )

    captured = []

    def fake_generate(self, messages, model_name, configuration):
        captured.append(messages)
        return "Contexto recebido"

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", fake_generate)

    guitar_response = client.post(
        f"/conversations/{guitar_conversation['id']}/chat",
        json={"content": "O que estamos desenvolvendo?"},
    )
    tennis_response = client.post(
        f"/conversations/{tennis_conversation['id']}/chat",
        json={"content": "O que estamos desenvolvendo?"},
    )

    assert guitar_response.status_code == 200
    assert tennis_response.status_code == 200
    assert len(captured) == 2

    guitar_context = str(captured[0])
    tennis_context = str(captured[1])

    assert "guitar" in guitar_context
    assert "gerar charts para guitarra" in guitar_context
    assert "tennis" not in guitar_context
    assert "rastrear movimento da raquete" not in guitar_context

    assert "tennis" in tennis_context
    assert "rastrear movimento da raquete" in tennis_context
    assert "guitar" not in tennis_context
    assert "gerar charts para guitarra" not in tennis_context


def test_conversation_history_does_not_leak_between_conversations() -> None:
    project = create_project(
        name="Shared Project",
        workspace="/tmp/shared-project",
        state={"project": "shared"},
    )
    model = create_model("Local Model", "ollama", "local:test")

    first = create_conversation(
        "Conversation A",
        model.id,
        project_id=project.id,
    )
    second = create_conversation(
        "Conversation B",
        model.id,
        project_id=project.id,
    )

    remember(
        type="project_state",
        key="shared_context",
        value="contexto permitido pelo projeto",
        source="conversation",
        project_id=project.id,
    )

    create_message(first.id, "user", "segredo da conversa A")
    create_message(first.id, "assistant", "resposta exclusiva A")
    create_message(second.id, "user", "segredo da conversa B")
    create_message(second.id, "assistant", "resposta exclusiva B")

    first_context = str(build_context(first.id))
    second_context = str(build_context(second.id))

    assert "segredo da conversa A" in first_context
    assert "resposta exclusiva A" in first_context
    assert "segredo da conversa B" not in first_context
    assert "resposta exclusiva B" not in first_context

    assert "segredo da conversa B" in second_context
    assert "resposta exclusiva B" in second_context
    assert "segredo da conversa A" not in second_context
    assert "resposta exclusiva A" not in second_context

    assert "contexto permitido pelo projeto" in first_context
    assert "contexto permitido pelo projeto" in second_context
