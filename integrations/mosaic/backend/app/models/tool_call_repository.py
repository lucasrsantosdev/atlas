import json
from datetime import datetime, timezone
from typing import Any

from app.db.database import get_connection
from app.models.tool_call import ToolCall
from app.core.state_transitions import TOOL_CALL_TRANSITIONS, validate_transition
from app.models.task_event_repository import create_task_event

ALLOWED_STATUSES = {
    "pending",
    "approved",
    "executing",
    "completed",
    "failed",
    "rejected",
    "cancelled",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_status(status: str) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid tool call status: {status}")


def create_tool_call(
    conversation_id: int,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    task_id: int | None = None,
    status: str = "pending",
) -> ToolCall:
    if not tool_name:
        raise ValueError("Tool name is required")
    _validate_status(status)
    if status != "pending":
        raise ValueError("New tool calls must start in pending status")
    tool_arguments = arguments or {}
    created_at = _utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tool_calls (
                conversation_id, task_id, tool_name, arguments,
                status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                task_id,
                tool_name,
                json.dumps(tool_arguments),
                status,
                created_at,
                created_at,
            ),
        )
        connection.commit()

    call = ToolCall(
        id=cursor.lastrowid,
        conversation_id=conversation_id,
        task_id=task_id,
        tool_name=tool_name,
        arguments=tool_arguments,
        status=status,
        created_at=created_at,
        updated_at=created_at,
    )
    if task_id is not None:
        create_task_event(
            task_id=task_id, conversation_id=conversation_id, tool_call_id=call.id,
            event_name="tool.proposed", message=f"Tool proposed: {tool_name}", component="tool",
            status="pending", metadata={"tool_name": tool_name, "arguments": tool_arguments},
        )
    return call


def get_tool_call(tool_call_id: int) -> ToolCall | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, conversation_id, task_id, tool_name, arguments,
                   status, created_at, updated_at
            FROM tool_calls
            WHERE id = ?
            """,
            (tool_call_id,),
        ).fetchone()

    return _row_to_tool_call(row) if row else None


def list_tool_calls(conversation_id: int) -> list[ToolCall]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, conversation_id, task_id, tool_name, arguments,
                   status, created_at, updated_at
            FROM tool_calls
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

    return [_row_to_tool_call(row) for row in rows]


def update_tool_call(tool_call_id: int, *, status: str) -> ToolCall | None:
    _validate_status(status)
    current = get_tool_call(tool_call_id)
    if current is None:
        return None

    validate_transition('tool call', current.status, status, TOOL_CALL_TRANSITIONS)
    updated_at = _utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tool_calls
            SET status = ?, updated_at = ?
            WHERE id = ? AND status = ?
            """,
            (status, updated_at, tool_call_id, current.status),
        )
        if cursor.rowcount != 1:
            raise ValueError("Concurrent tool call state change detected")
        connection.commit()

    updated = get_tool_call(tool_call_id)
    if updated is not None and updated.task_id is not None:
        create_task_event(
            task_id=updated.task_id, conversation_id=updated.conversation_id,
            tool_call_id=updated.id, event_name=f"tool.{status}",
            message=f"ToolCall {updated.id} status changed to {status}", component="tool",
            status=status, metadata={"tool_name": updated.tool_name},
            level="error" if status == "failed" else "warning" if status == "rejected" else "info",
        )
    return updated


def _row_to_tool_call(row) -> ToolCall:
    return ToolCall(
        id=row["id"],
        conversation_id=row["conversation_id"],
        task_id=row["task_id"],
        tool_name=row["tool_name"],
        arguments=json.loads(row["arguments"]),
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
