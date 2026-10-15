import json
from datetime import datetime, timezone
from typing import Any

from app.db.database import get_connection
from app.models.action import Action
from app.core.state_transitions import ACTION_TRANSITIONS, validate_transition

ALLOWED_STATUSES = {
    "pending",
    "approved",
    "executing",
    "completed",
    "rejected",
    "failed",
    "cancelled",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_status(status: str) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid action status: {status}")


def create_action(
    task_id: int,
    type: str,
    target: str | None = None,
    payload: dict[str, Any] | None = None,
    status: str = "pending",
    result: dict[str, Any] | None = None,
) -> Action:
    if not type:
        raise ValueError("Action type is required")
    _validate_status(status)
    if status != "pending":
        raise ValueError("New actions must start in pending status")
    action_payload = payload or {}
    created_at = _utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO actions (
                task_id, type, target, payload, status, result, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                type,
                target,
                json.dumps(action_payload),
                status,
                json.dumps(result) if result is not None else None,
                created_at,
                created_at,
            ),
        )
        connection.commit()

    return Action(
        id=cursor.lastrowid,
        task_id=task_id,
        type=type,
        target=target,
        payload=action_payload,
        status=status,
        result=result,
        created_at=created_at,
        updated_at=created_at,
    )


def get_action(action_id: int) -> Action | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, task_id, type, target, payload, status, result,
                   created_at, updated_at
            FROM actions
            WHERE id = ?
            """,
            (action_id,),
        ).fetchone()

    return _row_to_action(row) if row else None


def list_actions(task_id: int | None = None) -> list[Action]:
    with get_connection() as connection:
        if task_id is None:
            rows = connection.execute(
                """
                SELECT id, task_id, type, target, payload, status, result,
                       created_at, updated_at
                FROM actions
                ORDER BY id ASC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, task_id, type, target, payload, status, result,
                       created_at, updated_at
                FROM actions
                WHERE task_id = ?
                ORDER BY id ASC
                """,
                (task_id,),
            ).fetchall()

    return [_row_to_action(row) for row in rows]


def update_action(
    action_id: int,
    *,
    type: str | None = None,
    target: str | None = None,
    payload: dict[str, Any] | None = None,
    status: str | None = None,
    result: dict[str, Any] | None = None,
) -> Action | None:
    current = get_action(action_id)
    if current is None:
        return None

    new_type = current.type if type is None else type
    new_target = current.target if target is None else target
    new_payload = current.payload if payload is None else payload
    new_status = current.status if status is None else status
    new_result = current.result if result is None else result

    if not new_type:
        raise ValueError("Action type is required")
    if status is not None:
        validate_transition('action', current.status, new_status, ACTION_TRANSITIONS)
    _validate_status(new_status)
    updated_at = _utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE actions
            SET type = ?, target = ?, payload = ?, status = ?,
                result = ?, updated_at = ?
            WHERE id = ? AND status = ?
            """,
            (
                new_type,
                new_target,
                json.dumps(new_payload),
                new_status,
                json.dumps(new_result) if new_result is not None else None,
                updated_at,
                action_id,
                current.status,
            ),
        )
        if cursor.rowcount != 1:
            raise ValueError("Concurrent action state change detected")
        connection.commit()

    return get_action(action_id)


def delete_action(action_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM actions WHERE id = ?", (action_id,))
        connection.commit()
        return cursor.rowcount > 0


def _row_to_action(row) -> Action:
    return Action(
        id=row["id"],
        task_id=row["task_id"],
        type=row["type"],
        target=row["target"],
        payload=json.loads(row["payload"]),
        status=row["status"],
        result=json.loads(row["result"]) if row["result"] is not None else None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
