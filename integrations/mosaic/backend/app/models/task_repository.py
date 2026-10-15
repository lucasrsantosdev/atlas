import json
from datetime import datetime, timezone
from typing import Any

from app.db.database import get_connection
from app.models.task import Task
from app.core.state_transitions import TASK_TRANSITIONS, validate_transition
from app.models.task_event_repository import create_task_event

ALLOWED_TYPES = {"code_project", "document", "analysis", "report", "generic"}
ALLOWED_MODES = {"create", "agent"}
ALLOWED_STATUSES = {
    "pending",
    "planning",
    "awaiting_approval",
    "executing",
    "validating",
    "completed",
    "failed",
    "cancelled",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_task(
    conversation_id: int | None,
    project_id: int | None,
    type: str,
    mode: str,
    status: str,
) -> None:
    if conversation_id is None and project_id is None:
        raise ValueError("Task requires conversation_id or project_id")
    if type not in ALLOWED_TYPES:
        raise ValueError(f"Invalid task type: {type}")
    if mode not in ALLOWED_MODES:
        raise ValueError(f"Invalid task mode: {mode}")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid task status: {status}")


def create_task(
    type: str,
    mode: str,
    conversation_id: int | None = None,
    project_id: int | None = None,
    status: str = "pending",
    plan: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
) -> Task:
    if status != "pending":
        raise ValueError("New tasks must start in pending status")
    _validate_task(conversation_id, project_id, type, mode, status)
    created_at = _utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                conversation_id, project_id, type, mode, status,
                plan, result, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                project_id,
                type,
                mode,
                status,
                json.dumps(plan) if plan is not None else None,
                json.dumps(result) if result is not None else None,
                created_at,
                created_at,
            ),
        )
        connection.commit()

    task = Task(
        id=cursor.lastrowid,
        conversation_id=conversation_id,
        project_id=project_id,
        type=type,
        mode=mode,
        status=status,
        plan=plan,
        result=result,
        created_at=created_at,
        updated_at=created_at,
    )
    create_task_event(
        task_id=task.id, conversation_id=conversation_id, project_id=project_id,
        event_name="task.created", message="Task created", status="pending",
        metadata={"mode": mode, "type": type},
    )
    return task


def get_task(task_id: int) -> Task | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, conversation_id, project_id, type, mode, status,
                   plan, result, created_at, updated_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

    return _row_to_task(row) if row else None


def list_tasks(
    conversation_id: int | None = None,
    project_id: int | None = None,
) -> list[Task]:
    with get_connection() as connection:
        query = """
            SELECT id, conversation_id, project_id, type, mode, status,
                   plan, result, created_at, updated_at
            FROM tasks
        """
        conditions: list[str] = []
        parameters: list[int] = []

        if conversation_id is not None:
            conditions.append("conversation_id = ?")
            parameters.append(conversation_id)
        if project_id is not None:
            conditions.append("project_id = ?")
            parameters.append(project_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id ASC"
        rows = connection.execute(query, parameters).fetchall()

    return [_row_to_task(row) for row in rows]


def update_task(
    task_id: int,
    *,
    conversation_id: int | None = None,
    project_id: int | None = None,
    type: str | None = None,
    mode: str | None = None,
    status: str | None = None,
    plan: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
) -> Task | None:
    current = get_task(task_id)
    if current is None:
        return None

    new_conversation_id = current.conversation_id if conversation_id is None else conversation_id
    new_project_id = current.project_id if project_id is None else project_id
    new_type = current.type if type is None else type
    new_mode = current.mode if mode is None else mode
    new_status = current.status if status is None else status
    new_plan = current.plan if plan is None else plan
    new_result = current.result if result is None else result

    if status is not None and new_status != current.status:
        validate_transition("task", current.status, new_status, TASK_TRANSITIONS)
    _validate_task(
        new_conversation_id,
        new_project_id,
        new_type,
        new_mode,
        new_status,
    )
    updated_at = _utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET conversation_id = ?, project_id = ?, type = ?, mode = ?,
                status = ?, plan = ?, result = ?, updated_at = ?
            WHERE id = ? AND status = ?
            """,
            (
                new_conversation_id,
                new_project_id,
                new_type,
                new_mode,
                new_status,
                json.dumps(new_plan) if new_plan is not None else None,
                json.dumps(new_result) if new_result is not None else None,
                updated_at,
                task_id,
                current.status,
            ),
        )
        if cursor.rowcount != 1:
            raise ValueError("Concurrent task state change detected")
        connection.commit()

    updated = get_task(task_id)
    if status is not None and new_status != current.status:
        create_task_event(
            task_id=task_id, conversation_id=updated.conversation_id if updated else current.conversation_id,
            project_id=updated.project_id if updated else current.project_id,
            event_name="task.status_changed", message=f"Task status changed from {current.status} to {new_status}",
            status=new_status, metadata={"previous_status": current.status, "status": new_status},
            level="error" if new_status == "failed" else "warning" if new_status == "cancelled" else "info",
        )
    return updated


def delete_task(task_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()
        return cursor.rowcount > 0


def _row_to_task(row) -> Task:
    return Task(
        id=row["id"],
        conversation_id=row["conversation_id"],
        project_id=row["project_id"],
        type=row["type"],
        mode=row["mode"],
        status=row["status"],
        plan=json.loads(row["plan"]) if row["plan"] is not None else None,
        result=json.loads(row["result"]) if row["result"] is not None else None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
