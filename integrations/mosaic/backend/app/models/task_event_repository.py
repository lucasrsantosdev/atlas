import json
import re
from datetime import datetime, timezone
from typing import Any

from app.db.database import get_connection
from app.models.task_event import TaskEvent

_ALLOWED_LEVELS = {"debug", "info", "warning", "error"}
_SECRET_KEY = re.compile(r"(token|secret|password|credential|authorization|api[_-]?key|private[_-]?key)", re.I)
_MAX_MESSAGE = 500
_MAX_METADATA_CHARS = 4000


def _redact(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return "[depth-limited]"
    if isinstance(value, dict):
        return {str(key)[:100]: ("[REDACTED]" if _SECRET_KEY.search(str(key)) else _redact(item, depth + 1)) for key, item in list(value.items())[:50]}
    if isinstance(value, list):
        return [_redact(item, depth + 1) for item in value[:50]]
    if isinstance(value, str):
        return value[:1000]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:500]


def create_task_event(
    *, task_id: int, event_name: str, message: str, component: str = "task",
    level: str = "info", conversation_id: int | None = None,
    project_id: int | None = None, tool_call_id: int | None = None,
    action_id: int | None = None, duration_ms: int | None = None,
    status: str | None = None, metadata: dict[str, Any] | None = None,
) -> TaskEvent:
    if level not in _ALLOWED_LEVELS:
        raise ValueError(f"Invalid event level: {level}")
    if not event_name.strip() or not component.strip():
        raise ValueError("Event name and component are required")
    if duration_ms is not None and duration_ms < 0:
        raise ValueError("duration_ms must be non-negative")
    safe_metadata = _redact(metadata or {})
    encoded_metadata = json.dumps(safe_metadata, ensure_ascii=False, separators=(",", ":"))
    if len(encoded_metadata) > _MAX_METADATA_CHARS:
        encoded_metadata = json.dumps({"truncated": True, "preview": encoded_metadata[:_MAX_METADATA_CHARS - 40]})
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            """INSERT INTO task_events (
                task_id, conversation_id, project_id, tool_call_id, action_id,
                timestamp, level, component, event_name, message, duration_ms,
                status, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_id, conversation_id, project_id, tool_call_id, action_id,
             timestamp, level, component[:80], event_name[:120], message[:_MAX_MESSAGE],
             duration_ms, status[:80] if status else None, encoded_metadata),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM task_events WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _row_to_event(row)


def list_task_events(task_id: int, *, after_id: int = 0, limit: int = 100) -> list[TaskEvent]:
    if after_id < 0:
        raise ValueError("after_id must be non-negative")
    if not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200")
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM task_events WHERE task_id = ? AND id > ? ORDER BY id ASC LIMIT ?",
            (task_id, after_id, limit),
        ).fetchall()
    return [_row_to_event(row) for row in rows]


def _row_to_event(row) -> TaskEvent:
    return TaskEvent(
        id=row["id"], task_id=row["task_id"], conversation_id=row["conversation_id"],
        project_id=row["project_id"], tool_call_id=row["tool_call_id"], action_id=row["action_id"],
        timestamp=row["timestamp"], level=row["level"], component=row["component"],
        event_name=row["event_name"], message=row["message"], duration_ms=row["duration_ms"],
        status=row["status"], metadata=json.loads(row["metadata"]),
    )
