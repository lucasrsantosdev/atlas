from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.project import Project
from app.models.project_repository import (
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from app.services.project import create_project_with_workspace
from app.services.agent_config import get_agent_config, save_agent_config
from app.context.artifacts import list_workspace_artifacts, read_workspace_excerpt
from app.context.search import search_workspace_artifacts


class ProjectCreate(BaseModel):
    name: str
    workspace: str
    description: str | None = None
    metadata: dict[str, Any] = {}
    state: dict[str, Any] = {}


class AgentSkill(BaseModel):
    name: str
    content: str = ""
    enabled: bool = True


class AgentConfigUpdate(BaseModel):
    instructions: str = ""
    skills: list[AgentSkill] = []


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    workspace: str | None = None
    metadata: dict[str, Any] | None = None
    state: dict[str, Any] | None = None


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=Project)
def create_project_endpoint(payload: ProjectCreate) -> Project:
    try:
        return create_project_with_workspace(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[Project])
def list_projects_endpoint() -> list[Project]:
    return list_projects()


@router.get("/{project_id}", response_model=Project)
def get_project_endpoint(project_id: int) -> Project:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=Project)
def update_project_endpoint(project_id: int, payload: ProjectUpdate) -> Project:
    try:
        project = update_project(project_id, **payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project_endpoint(project_id: int) -> dict[str, bool]:
    if not delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}


@router.get("/{project_id}/agent-config")
def get_project_agent_config_endpoint(project_id: int) -> dict:
    try:
        config = get_agent_config(project_id)
    except (OSError, UnicodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if config is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return config


@router.put("/{project_id}/agent-config")
def save_project_agent_config_endpoint(
    project_id: int, payload: AgentConfigUpdate,
) -> dict:
    try:
        config = save_agent_config(
            project_id,
            instructions=payload.instructions,
            skills=[skill.model_dump() for skill in payload.skills],
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if config is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return config


@router.get("/{project_id}/artifacts")
def list_project_artifacts_endpoint(project_id: int) -> dict:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        return list_workspace_artifacts(project.workspace)
    except (OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{project_id}/artifacts/excerpt")
def read_project_artifact_excerpt_endpoint(
    project_id: int, path: str, start_line: int = 1, max_lines: int = 200,
) -> dict:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        return read_workspace_excerpt(
            project.workspace, path, start_line=start_line, max_lines=max_lines,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{project_id}/artifacts/search")
def search_project_artifacts_endpoint(
    project_id: int, q: str, max_results: int = 10,
) -> dict:
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        return search_workspace_artifacts(
            project.workspace, q, max_results=max_results,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
