import pytest
from fastapi.testclient import TestClient

from app.db.database import init_db
from app.main import app
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_same_ollama_provider_supports_user_defined_local_models(
    client: TestClient,
    monkeypatch,
) -> None:
    qwen = create_model("Qwen 3B", "ollama", "qwen3:3b")
    llama = create_model("Llama Local", "ollama", "llama3.2:3b")
    custom = create_model("Meu Modelo Local", "ollama", "meu-modelo:8b")

    conversation = client.post(
        "/conversations",
        json={"title": "Local models", "model_id": qwen.id},
    ).json()

    calls = []

    def fake_generate(self, messages, model_name, configuration):
        calls.append(model_name)
        return f"Resposta de {model_name}"

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", fake_generate)

    first = client.post(
        f"/conversations/{conversation['id']}/chat",
        json={"content": "Qwen"},
    )
    assert first.status_code == 200

    switched_to_llama = client.patch(
        f"/conversations/{conversation['id']}",
        json={"model_id": llama.id},
    )
    assert switched_to_llama.status_code == 200
    assert switched_to_llama.json()["model_id"] == llama.id

    second = client.post(
        f"/conversations/{conversation['id']}/chat",
        json={"content": "Llama"},
    )
    assert second.status_code == 200

    switched_to_custom = client.patch(
        f"/conversations/{conversation['id']}",
        json={"model_id": custom.id},
    )
    assert switched_to_custom.status_code == 200
    assert switched_to_custom.json()["model_id"] == custom.id

    third = client.post(
        f"/conversations/{conversation['id']}/chat",
        json={"content": "Meu modelo"},
    )
    assert third.status_code == 200

    assert calls == ["qwen3:3b", "llama3.2:3b", "meu-modelo:8b"]
