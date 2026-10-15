import sqlite3

import pytest

from app.api.tasks import TaskUpdate, cancel_task_endpoint
from app.db.database import get_connection, init_db
from pydantic import ValidationError
from app.models.project_repository import create_project
from app.models.task_repository import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    update_task,
)


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def test_task_persists_with_project() -> None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO projects (
                name, workspace, metadata, state, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Mosaic",
                "/tmp/mosaic",
                "{}",
                "{}",
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
            ),
        )
        project_id = cursor.lastrowid
        connection.commit()

    task = create_task(
        type="code_project",
        mode="create",
        project_id=project_id,
        plan={"steps": ["implement task"]},
    )

    assert get_task(task.id) == task
    assert list_tasks() == [task]
    assert task.status == "pending"


def test_task_can_link_to_conversation() -> None:
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO models (name, provider, model_name) VALUES (?, ?, ?)",
            ("Qwen 3B", "ollama", "qwen3:3b"),
        )
        model_id = cursor.lastrowid
        cursor = connection.execute(
            """
            INSERT INTO conversations (
                title, mode, model_id, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Task chat",
                "chat",
                model_id,
                "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00",
            ),
        )
        conversation_id = cursor.lastrowid
        connection.commit()

    task = create_task(
        type="analysis",
        mode="agent",
        conversation_id=conversation_id,
    )

    assert task.conversation_id == conversation_id
    assert task.project_id is None


def test_task_requires_relationship() -> None:
    with pytest.raises(ValueError, match="conversation_id or project_id"):
        create_task(type="generic", mode="create")


def test_task_rejects_invalid_lifecycle_values() -> None:
    with pytest.raises(ValueError):
        create_task(type="unknown", mode="create", project_id=1)

    with pytest.raises(ValueError):
        create_task(type="generic", mode="unknown", project_id=1)

    with pytest.raises(ValueError):
        create_task(type="generic", mode="create", project_id=1, status="unknown")


def test_task_update_and_delete() -> None:
    project = create_project("Mosaic", "/tmp/mosaic")
    task = create_task(type="document", mode="create", project_id=project.id)

    updated = update_task(
        task.id,
        status="planning",
        plan={"steps": ["draft"]},
        result={"artifact": "draft.md"},
    )

    assert updated is not None
    assert updated.status == "planning"
    assert updated.plan == {"steps": ["draft"]}
    assert updated.result == {"artifact": "draft.md"}
    assert updated.updated_at >= task.updated_at

    assert delete_task(task.id) is True
    assert get_task(task.id) is None


def test_database_enforces_relationship_check() -> None:
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO tasks (
                    type, mode, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "generic",
                    "create",
                    "pending",
                    "2026-01-01T00:00:00+00:00",
                    "2026-01-01T00:00:00+00:00",
                ),
            )



def test_task_status_cannot_be_changed_through_generic_patch() -> None:
    with pytest.raises(ValidationError):
        TaskUpdate.model_validate({"status": "completed"})


def test_task_can_be_cancelled_through_core_endpoint() -> None:
    project = create_project("Mosaic", "/tmp/mosaic")
    task = create_task(type="generic", mode="agent", project_id=project.id)
    cancelled = cancel_task_endpoint(task.id)
    assert cancelled.status == "cancelled"
