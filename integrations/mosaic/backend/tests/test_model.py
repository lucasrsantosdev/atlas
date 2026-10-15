import sqlite3

import pytest

from app.db.database import init_db
from app.models.repository import create_model, get_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_model_creation_and_persistence() -> None:
    created = create_model(
        name="Qwen 3B",
        provider="ollama",
        model_name="qwen3:3b",
        configuration={"temperature": 0.2},
        enabled=True,
    )

    recovered = get_model(created.id)

    assert created.name == "Qwen 3B"
    assert created.provider == "ollama"
    assert created.model_name == "qwen3:3b"
    assert created.configuration == {"temperature": 0.2}
    assert created.enabled is True
    assert recovered == created


def test_model_enabled_can_be_disabled() -> None:
    created = create_model(
        name="Qwen 3B",
        provider="ollama",
        model_name="qwen3:3b",
        enabled=False,
    )

    recovered = get_model(created.id)

    assert recovered is not None
    assert recovered.enabled is False
    assert recovered.configuration == {}


def test_model_provider_and_model_name_must_be_unique() -> None:
    create_model(
        name="Qwen 3B",
        provider="ollama",
        model_name="qwen3:3b",
    )

    with pytest.raises(sqlite3.IntegrityError):
        create_model(
            name="Qwen 3B Alternative",
            provider="ollama",
            model_name="qwen3:3b",
        )
