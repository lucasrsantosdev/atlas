import pytest

from app.db.database import get_connection, init_db
from app.models.project_repository import create_project
from app.models.task_repository import create_task, update_task
from app.models.task_event_repository import create_task_event, list_task_events
from app.api.tasks import list_task_events_endpoint


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "events.db")
    init_db()


def test_task_creation_and_status_change_are_persisted_in_order():
    project = create_project("Events", "/tmp/events")
    task = create_task(type="generic", mode="agent", project_id=project.id)
    update_task(task.id, status="executing")
    update_task(task.id, status="completed", result={"output": "done"})

    events = list_task_events(task.id)
    assert [event.event_name for event in events] == [
        "task.created", "task.status_changed", "task.status_changed"
    ]
    assert [event.id for event in events] == sorted(event.id for event in events)
    assert events[1].metadata["previous_status"] == "pending"
    assert events[2].status == "completed"


def test_event_metadata_redacts_secret_fields_and_bounds_payload():
    project = create_project("Events", "/tmp/events")
    task = create_task(type="generic", mode="agent", project_id=project.id)
    event = create_task_event(
        task_id=task.id, project_id=project.id, event_name="test.redaction",
        message="redaction test", metadata={"api_key": "do-not-store", "ok": "yes"},
    )
    with get_connection() as connection:
        row = connection.execute("SELECT metadata FROM task_events WHERE id = ?", (event.id,)).fetchone()
    assert "do-not-store" not in row["metadata"]
    assert event.metadata["api_key"] == "[REDACTED]"


def test_events_api_returns_ordered_events_after_cursor():
    project = create_project("Events", "/tmp/events")
    task = create_task(type="generic", mode="agent", project_id=project.id)
    update_task(task.id, status="executing")

    events = list_task_events_endpoint(task.id, after_id=0, limit=10)
    assert len(events) == 2
    next_events = list_task_events_endpoint(task.id, after_id=events[0].id, limit=10)
    assert [event.id for event in next_events] == [events[1].id]


def test_event_cursor_and_limit_are_validated():
    project = create_project("Events", "/tmp/events")
    task = create_task(type="generic", mode="agent", project_id=project.id)
    first = list_task_events(task.id)[0]
    assert list_task_events(task.id, after_id=first.id) == []
    with pytest.raises(ValueError, match="after_id"):
        list_task_events(task.id, after_id=-1)
    with pytest.raises(ValueError, match="limit"):
        list_task_events(task.id, limit=201)
