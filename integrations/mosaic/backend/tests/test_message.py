import sqlite3

import pytest

from app.db.database import get_connection, init_db
from app.models.conversation_repository import create_conversation
from app.models.message_repository import create_message, get_message, list_messages
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_message_creation_and_persistence() -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("Teste", model.id)
    created = create_message(conversation.id, "user", "Olá, Mosaic", {"source": "test"})

    recovered = get_message(created.id)

    assert created.conversation_id == conversation.id
    assert created.role == "user"
    assert created.content == "Olá, Mosaic"
    assert created.metadata == {"source": "test"}
    assert recovered == created


def test_message_metadata_defaults_to_empty_object() -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("Teste", model.id)
    created = create_message(conversation.id, "assistant", "Olá")
    assert created.metadata == {}


def test_message_roles_are_restricted() -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("Teste", model.id)
    with pytest.raises(ValueError):
        create_message(conversation.id, "invalid", "Mensagem")


def test_messages_are_listed_in_creation_order() -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("Teste", model.id)
    first = create_message(conversation.id, "user", "Primeira")
    second = create_message(conversation.id, "assistant", "Segunda")
    assert list_messages(conversation.id) == [first, second]


def test_message_requires_existing_conversation() -> None:
    with pytest.raises(sqlite3.IntegrityError):
        create_message(999999, "user", "Mensagem")


def test_deleting_conversation_cascades_messages() -> None:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = create_conversation("Teste", model.id)
    create_message(conversation.id, "user", "Mensagem")

    with get_connection() as connection:
        connection.execute("DELETE FROM conversations WHERE id = ?", (conversation.id,))
        connection.commit()

    assert list_messages(conversation.id) == []
