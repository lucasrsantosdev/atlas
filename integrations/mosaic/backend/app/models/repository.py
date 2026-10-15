import json
from typing import Any

from app.db.database import get_connection
from app.models.model import Model


def create_model(
    name: str,
    provider: str,
    model_name: str,
    configuration: dict[str, Any] | None = None,
    enabled: bool = True,
) -> Model:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO models (name, provider, model_name, configuration, enabled)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                provider,
                model_name,
                json.dumps(configuration or {}),
                int(enabled),
            ),
        )
        connection.commit()

        return Model(
            id=cursor.lastrowid,
            name=name,
            provider=provider,
            model_name=model_name,
            configuration=configuration or {},
            enabled=enabled,
        )


def list_models() -> list[Model]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, provider, model_name, configuration, enabled
            FROM models
            ORDER BY id
            """
        ).fetchall()

    return [
        Model(
            id=row["id"],
            name=row["name"],
            provider=row["provider"],
            model_name=row["model_name"],
            configuration=json.loads(row["configuration"]),
            enabled=bool(row["enabled"]),
        )
        for row in rows
    ]


def get_model(model_id: int) -> Model | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, provider, model_name, configuration, enabled
            FROM models
            WHERE id = ?
            """,
            (model_id,),
        ).fetchone()

    if row is None:
        return None

    return Model(
        id=row["id"],
        name=row["name"],
        provider=row["provider"],
        model_name=row["model_name"],
        configuration=json.loads(row["configuration"]),
        enabled=bool(row["enabled"]),
    )

def update_model(
    model_id: int,
    name: str | None = None,
    configuration: dict[str, Any] | None = None,
    enabled: bool | None = None,
) -> Model:
    current = get_model(model_id)
    if current is None:
        raise ValueError("Model not found")

    next_name = name if name is not None else current.name
    next_configuration = configuration if configuration is not None else current.configuration
    next_enabled = enabled if enabled is not None else current.enabled

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE models
            SET name = ?, configuration = ?, enabled = ?
            WHERE id = ?
            """,
            (next_name, json.dumps(next_configuration), int(next_enabled), model_id),
        )
        connection.commit()

    return Model(
        id=current.id,
        name=next_name,
        provider=current.provider,
        model_name=current.model_name,
        configuration=next_configuration,
        enabled=next_enabled,
    )
