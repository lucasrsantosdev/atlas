from pathlib import Path

from app.models.project import Project
from app.models.project_repository import create_project


def create_project_with_workspace(
    name: str,
    workspace: str,
    description: str | None = None,
    metadata: dict | None = None,
    state: dict | None = None,
) -> Project:
    Path(workspace).mkdir(parents=True, exist_ok=True)
    return create_project(
        name=name,
        workspace=workspace,
        description=description,
        metadata=metadata,
        state=state,
    )
