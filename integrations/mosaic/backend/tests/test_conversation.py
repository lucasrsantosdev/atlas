import sqlite3

import pytest

from app.db.database import get_connection, init_db
from app.models.conversation_repository import (
    create_conversation,
    get_conversation,
)
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_foreign_keys_are_enabled() -> None:
    with get_connection() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_conversation_creation_and_persistence() -> None:
    model = create_model(
        name="Qwen 3B",
        provider="ollama",
        model_name="qwen3:3b",
    )

    created = create_conversation(
        title="Primeira conversa",
        model_id=model.id,
    )

    recovered = get_conversation(created.id)

    assert created.title == "Primeira conversa"
    assert created.mode == "chat"
    assert created.model_id == model.id
    assert created.project_id is None
    assert recovered == created


def test_conversation_can_reference_a_project() -> None:
    model = create_model(
        name="Qwen 3B",
        provider="ollama",
        model_name="qwen3:3b",
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO projects (
                name,
                workspace,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "Projeto de teste",
                "/tmp/mosaic-test",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
            ),
        )
        project_id = cursor.lastrowid
        connection.commit()

    created = create_conversation(
        title="Conversa no projeto",
        model_id=model.id,
        project_id=project_id,
    )

    assert created.project_id == project_id
    assert get_conversation(created.id) == created


def test_project_delete_sets_conversation_project_to_null() -> None:
    model = create_model(
        name="Qwen 3B",
        provider="ollama",
        model_name="qwen3:3b",
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO projects (
                name,
                workspace,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "Projeto de teste",
                "/tmp/mosaic-test",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
            ),
        )
        project_id = cursor.lastrowid
        connection.commit()

    created = create_conversation(
        title="Conversa no projeto",
        model_id=model.id,
        project_id=project_id,
    )

    with get_connection() as connection:
        connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        connection.commit()

    recovered = get_conversation(created.id)

    assert recovered is not None
    assert recovered.project_id is None


def test_conversation_requires_existing_model() -> None:
    with pytest.raises(sqlite3.IntegrityError):
        create_conversation(
            title="Sem modelo",
            model_id=999999,
        )
  