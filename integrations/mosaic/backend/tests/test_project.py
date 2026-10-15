import pytest

from app.db.database import get_connection, init_db
from app.models.project_repository import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from app.services.project import create_project_with_workspace


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_project_persists_metadata_and_state() -> None:
    project = create_project(
        name="Mosaic",
        workspace="/tmp/mosaic",
        description="Core project",
        metadata={"kind": "software"},
        state={"phase": "project"},
    )

    assert get_project(project.id) == project
    assert list_projects() == [project]


def test_project_creation_creates_workspace(tmp_path) -> None:
    workspace = tmp_path / "workspace"

    project = create_project_with_workspace(
        name="Mosaic",
        workspace=str(workspace),
    )

    assert workspace.is_dir()
    assert project.workspace == str(workspace)


def test_project_update_changes_updated_at() -> None:
    project = create_project("Mosaic", "/tmp/mosaic")

    updated = update_project(
        project.id,
        description="Updated",
        state={"status": "active"},
    )

    assert updated is not None
    assert updated.description == "Updated"
    assert updated.state == {"status": "active"}
    assert updated.updated_at >= project.updated_at


def test_project_delete_sets_conversation_and_memory_project_id_to_null() -> None:
    project = create_project("Mosaic", "/tmp/mosaic")

    with get_connection() as connection:
        connection.execute(
            "INSERT INTO models (name, provider, model_name) VALUES (?, ?, ?)",
            ("Qwen 3B", "ollama", "qwen3:3b"),
        )
        connection.execute(
            """
            INSERT INTO conversations (title, mode, model_id, project_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("Chat", "chat", 1, project.id, "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00"),
        )
        connection.execute(
            """
            INSERT INTO memories (
                project_id, type, key, value, source, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (project.id, "project_state", "status", "active", "system",
             "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00"),
        )
        connection.commit()

    assert delete_project(project.id) is True

    with get_connection() as connection:
        conversation = connection.execute(
            "SELECT project_id FROM conversations WHERE id = 1"
        ).fetchone()
        memory = connection.execute(
            "SELECT project_id FROM memories WHERE id = 1"
        ).fetchone()

    assert conversation["project_id"] is None
    assert memory["project_id"] is None
