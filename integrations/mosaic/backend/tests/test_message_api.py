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


def test_message_api_create_and_list(client: TestClient) -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = client.post(
        "/conversations", json={"title": "API test", "model_id": model.id}
    )
    assert conversation.status_code == 200
    conversation_id = conversation.json()["id"]

    created = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Olá", "metadata": {"source": "api"}},
    )

    assert created.status_code == 200
    message = created.json()
    assert message["conversation_id"] == conversation_id
    assert message["role"] == "user"
    assert message["content"] == "Olá"
    assert message["metadata"] == {"source": "api"}

    listed = client.get(f"/conversations/{conversation_id}/messages")
    assert listed.status_code == 200
    assert listed.json() == [message]


def test_message_api_rejects_invalid_role(client: TestClient) -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = client.post(
        "/conversations", json={"title": "API test", "model_id": model.id}
    )
    conversation_id = conversation.json()["id"]

    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"role": "invalid", "content": "Mensagem"},
    )
    assert response.status_code == 400


def test_message_api_rejects_unknown_conversation(client: TestClient) -> None:
    response = client.post(
        "/conversations/999999/messages",
        json={"role": "user", "content": "Mensagem"},
    )
    assert response.status_code == 400
