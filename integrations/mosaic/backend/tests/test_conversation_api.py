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


def test_conversation_api_crud(client: TestClient) -> None:
    model = create_model(
        name="Qwen 3B",
        provider="ollama",
        model_name="qwen3:3b",
    )

    created = client.post(
        "/conversations",
        json={"title": "API test", "model_id": model.id},
    )

    assert created.status_code == 200
    conversation = created.json()
    assert conversation["title"] == "API test"
    assert conversation["mode"] == "chat"
    assert conversation["model_id"] == model.id
    assert conversation["project_id"] is None

    conversation_id = conversation["id"]

    listed = client.get("/conversations")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == conversation_id

    recovered = client.get(f"/conversations/{conversation_id}")
    assert recovered.status_code == 200
    assert recovered.json() == conversation

    updated = client.patch(
        f"/conversations/{conversation_id}",
        json={"title": "API test updated"},
    )

    assert updated.status_code == 200
    assert updated.json()["title"] == "API test updated"
    assert updated.json()["model_id"] == model.id


def test_conversation_api_returns_404_for_unknown_conversation(
    client: TestClient,
) -> None:
    response = client.get("/conversations/999999")

    assert response.status_code == 404


def test_conversation_api_rejects_unknown_model(client: TestClient) -> None:
    response = client.post(
        "/conversations",
        json={"title": "Invalid", "model_id": 999999},
    )

    assert response.status_code == 400
