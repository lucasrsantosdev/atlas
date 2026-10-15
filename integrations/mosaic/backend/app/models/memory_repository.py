from datetime import datetime, timezone

from app.db.database import get_connection
from app.models.memory import Memory


ALLOWED_TYPES = {
    "user_fact",
    "user_preference",
    "user_claim",
    "project_state",
    "instruction",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_memory(
    type: str,
    key: str,
    value: str,
    source: str,
    project_id: int | None = None,
    confidence: float | None = None,
) -> Memory:
    if type not in ALLOWED_TYPES:
        raise ValueError(f"Invalid memory type: {type}")
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ValueError("Memory confidence must be between 0.0 and 1.0")

    created_at = _utc_now()
    updated_at = created_at

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO memories (
                project_id, type, key, value, source, confidence, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, type, key, value, source, confidence, created_at, updated_at),
        )
        connection.commit()

    return Memory(
        id=cursor.lastrowid,
        project_id=project_id,
        type=type,
        key=key,
        value=value,
        source=source,
        confidence=confidence,
        created_at=created_at,
        updated_at=updated_at,
    )


def get_memory(memory_id: int) -> Memory | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, project_id, type, key, value, source, confidence, created_at, updated_at
            FROM memories
            WHERE id = ?
            """,
            (memory_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_memory(row)


def list_memories(project_id: int | None = None) -> list[Memory]:
    with get_connection() as connection:
        if project_id is None:
            rows = connection.execute(
                """
                SELECT id, project_id, type, key, value, source, confidence, created_at, updated_at
                FROM memories
                ORDER BY id ASC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, project_id, type, key, value, source, confidence, created_at, updated_at
                FROM memories
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()

    return [_row_to_memory(row) for row in rows]


def _row_to_memory(row) -> Memory:
    return Memory(
        id=row["id"],
        project_id=row["project_id"],
        type=row["type"],
        key=row["key"],
        value=row["value"],
        source=row["source"],
        confidence=row["confidence"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def update_memory(
    memory_id: int,
    *,
    type: str | None = None,
    key: str | None = None,
    value: str | None = None,
    source: str | None = None,
    project_id: int | None = None,
    confidence: float | None = None,
    clear_project_id: bool = False,
) -> Memory | None:
    current = get_memory(memory_id)
    if current is None:
        return None

    new_type = current.type if type is None else type
    if new_type not in ALLOWED_TYPES:
        raise ValueError(f"Invalid memory type: {new_type}")
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ValueError("Memory confidence must be between 0.0 and 1.0")

    new_project_id = None if clear_project_id else (
        current.project_id if project_id is None else project_id
    )
    updated_at = _utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE memories
            SET project_id = ?, type = ?, key = ?, value = ?, source = ?,
                confidence = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                new_project_id,
                new_type,
                current.key if key is None else key,
                current.value if value is None else value,
                current.source if source is None else source,
                confidence if confidence is not None else current.confidence,
                updated_at,
                memory_id,
            ),
        )
        connection.commit()

    return get_memory(memory_id)


def delete_memory(memory_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM memories WHERE id = ?",
            (memory_id,),
        )
        connection.commit()
        return cursor.rowcount > 0
