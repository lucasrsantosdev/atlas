from datetime import datetime, timezone

from app.db.database import get_connection
from app.models.conversation import Conversation


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_conversation(
    title: str,
    model_id: int,
    project_id: int | None = None,
    mode: str = "chat",
) -> Conversation:
    created_at = _utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO conversations (
                title,
                mode,
                model_id,
                project_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, mode, model_id, project_id, created_at, created_at),
        )
        connection.commit()

        return Conversation(
            id=cursor.lastrowid,
            title=title,
            mode=mode,
            model_id=model_id,
            project_id=project_id,
            created_at=created_at,
            updated_at=created_at,
        )


def get_conversation(conversation_id: int) -> Conversation | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                title,
                mode,
                model_id,
                project_id,
                created_at,
                updated_at
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        ).fetchone()

    if row is None:
        return None

    return Conversation(
        id=row["id"],
        title=row["title"],
        mode=row["mode"],
        model_id=row["model_id"],
        project_id=row["project_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def list_conversations() -> list[Conversation]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                title,
                mode,
                model_id,
                project_id,
                created_at,
                updated_at
            FROM conversations
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

    return [
        Conversation(
            id=row["id"],
            title=row["title"],
            mode=row["mode"],
            model_id=row["model_id"],
            project_id=row["project_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        for row in rows
    ]


def update_conversation(
    conversation_id: int,
    *,
    title: str | None = None,
    model_id: int | None = None,
    project_id: int | None = None,
) -> Conversation | None:
    current = get_conversation(conversation_id)
    if current is None:
        return None

    new_title = current.title if title is None else title
    new_model_id = current.model_id if model_id is None else model_id
    new_project_id = current.project_id if project_id is None else project_id
    updated_at = _utc_now()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE conversations
            SET title = ?,
                model_id = ?,
                project_id = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (new_title, new_model_id, new_project_id, updated_at, conversation_id),
        )
        connection.commit()

    return get_conversation(conversation_id)
