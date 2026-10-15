import json
from datetime import datetime, timezone
from typing import Any

from app.db.database import get_connection
from app.models.message import Message


ALLOWED_ROLES = {"user", "assistant", "system", "tool"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_message(
    conversation_id: int,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> Message:
    if role not in ALLOWED_ROLES:
        raise ValueError(f"Invalid message role: {role}")

    message_metadata = metadata or {}
    created_at = _utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO messages (
                conversation_id, role, content, created_at, metadata
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, role, content, created_at, json.dumps(message_metadata)),
        )
        connection.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (created_at, conversation_id),
        )
        connection.commit()

        return Message(
            id=cursor.lastrowid,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=created_at,
            metadata=message_metadata,
        )


def get_message(message_id: int) -> Message | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, conversation_id, role, content, created_at, metadata
            FROM messages
            WHERE id = ?
            """,
            (message_id,),
        ).fetchone()

    if row is None:
        return None

    return Message(
        id=row["id"],
        conversation_id=row["conversation_id"],
        role=row["role"],
        content=row["content"],
        created_at=row["created_at"],
        metadata=json.loads(row["metadata"]),
    )


def list_messages(conversation_id: int) -> list[Message]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, conversation_id, role, content, created_at, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

    return [
        Message(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
            metadata=json.loads(row["metadata"]),
        )
        for row in rows
    ]
