import pytest
from fastapi.testclient import TestClient

from app.db.database import init_db
from app.main import app


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_models_api_lists_and_retrieves_models(client: TestClient) -> None:
    created = client.post(
        "/models",
        json={
            "name": "Qwen 3B",
            "provider": "ollama",
            "model_name": "qwen3:3b",
            "configuration": {"temperature": 0.2},
        },
    )

    assert created.status_code == 200
    model = created.json()
    assert model["name"] == "Qwen 3B"
    assert model["provider"] == "ollama"
    assert model["model_name"] == "qwen3:3b"
    assert model["configuration"] == {"temperature": 0.2}
    assert model["enabled"] is True

    listed = client.get("/models")
    assert listed.status_code == 200
    assert listed.json() == [model]

    recovered = client.get(f"/models/{model['id']}")
    assert recovered.status_code == 200
    assert recovered.json() == model


def test_models_api_supports_disabled_models(client: TestClient) -> None:
    response = client.post(
        "/models",
        json={
            "name": "Disabled Model",
            "provider": "ollama",
            "model_name": "disabled:model",
            "enabled": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["enabled"] is False


def test_models_api_rejects_duplicate_provider_model(client: TestClient) -> None:
    payload = {
        "name": "Qwen 3B",
        "provider": "ollama",
        "model_name": "qwen3:3b",
    }

    first = client.post("/models", json=payload)
    second = client.post(
        "/models",
        json={**payload, "name": "Qwen Alternative"},
    )

    assert first.status_code == 200
    assert second.status_code == 400


def test_models_api_returns_404_for_unknown_model(client: TestClient) -> None:
    response = client.get("/models/999999")
    assert response.status_code == 404
