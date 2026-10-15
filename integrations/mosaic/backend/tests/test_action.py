import pytest

from app.db.database import get_connection, init_db
from app.models.action_repository import create_action, get_action, list_actions
from app.models.project_repository import create_project
from app.models.task_repository import create_task
from app.permissions import (
    approve_action,
    begin_action,
    cancel_action,
    complete_action,
    fail_action,
    reject_action,
)


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


def _task():
    project = create_project("Mosaic", "/tmp/mosaic")
    return create_task(type="generic", mode="create", project_id=project.id)


def test_action_persists_and_lists_by_task() -> None:
    task = _task()
    action = create_action(
        task_id=task.id,
        type="write_file",
        target="README.md",
        payload={"content": "hello"},
    )

    assert get_action(action.id) == action
    assert list_actions(task.id) == [action]
    assert action.status == "pending"


def test_action_lifecycle_and_permission_transitions() -> None:
    task = _task()
    action = create_action(task.id, "write_file")

    action = approve_action(action)
    assert action.status == "approved"

    action = begin_action(action)
    assert action.status == "executing"

    action = complete_action(action, {"path": "README.md"})
    assert action.status == "completed"
    assert action.result == {"path": "README.md"}


def test_rejection_failure_and_cancellation() -> None:
    task = _task()

    rejected = reject_action(create_action(task.id, "delete_file"))
    assert rejected.status == "rejected"

    failed = fail_action(begin_action(approve_action(create_action(task.id, "write_file"))))
    assert failed.status == "failed"

    cancelled = cancel_action(create_action(task.id, "run"))
    assert cancelled.status == "cancelled"


def test_invalid_transition_is_rejected() -> None:
    task = _task()
    action = create_action(task.id, "write_file")

    with pytest.raises(ValueError):
        complete_action(action, {"ok": True})

    approved = approve_action(action)
    with pytest.raises(ValueError):
        approve_action(approved)


def test_action_cascades_with_task() -> None:
    task = _task()
    action = create_action(task.id, "write_file")

    with get_connection() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task.id,))
        connection.commit()

    assert get_action(action.id) is None
