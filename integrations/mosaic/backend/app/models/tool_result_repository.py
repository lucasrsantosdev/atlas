import json
from datetime import datetime, timezone
from typing import Any

from app.db.database import get_connection
from app.models.tool_result import ToolResult

ALLOWED_STATUSES = {"completed", "failed"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_tool_result(
    tool_call_id: int,
    status: str,
    data: dict[str, Any] | None = None,
    error: str | None = None,
) -> ToolResult:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid tool result status: {status}")

    if status == "completed" and (data is None or error is not None):
        raise ValueError("Completed ToolResult requires data and no error")
    if status == "failed" and (data is not None or error is None):
        raise ValueError("Failed ToolResult requires error and no data")

    created_at = _utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tool_results (
                tool_call_id, status, data, error, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                tool_call_id,
                status,
                json.dumps(data) if data is not None else None,
                error,
                created_at,
            ),
        )
        connection.commit()

    return ToolResult(
        id=cursor.lastrowid,
        tool_call_id=tool_call_id,
        status=status,
        data=data,
        error=error,
        created_at=created_at,
    )


def get_tool_result(tool_result_id: int) -> ToolResult | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, tool_call_id, status, data, error, created_at
            FROM tool_results
            WHERE id = ?
            """,
            (tool_result_id,),
        ).fetchone()

    return _row_to_tool_result(row) if row else None


def list_tool_results(tool_call_id: int) -> list[ToolResult]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, tool_call_id, status, data, error, created_at
            FROM tool_results
            WHERE tool_call_id = ?
            ORDER BY id ASC
            """,
            (tool_call_id,),
        ).fetchall()

    return [_row_to_tool_result(row) for row in rows]


def _row_to_tool_result(row) -> ToolResult:
    return ToolResult(
        id=row["id"],
        tool_call_id=row["tool_call_id"],
        status=row["status"],
        data=json.loads(row["data"]) if row["data"] is not None else None,
        error=row["error"],
        created_at=row["created_at"],
    )
