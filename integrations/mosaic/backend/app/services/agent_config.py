from pathlib import Path
from typing import Any

from app.models.project import Project
from app.models.project_repository import get_project, update_project

MAX_INSTRUCTIONS_CHARS = 12_000
MAX_SKILLS = 12
MAX_SKILL_NAME_CHARS = 80
MAX_SKILL_CONTENT_CHARS = 4_000
MAX_ENABLED_SKILL_TOTAL_CHARS = 12_000


def _workspace(project: Project) -> Path:
    root = Path(project.workspace).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError("Project workspace does not exist or is not a directory")
    return root


def _instructions_path(project: Project) -> Path:
    root = _workspace(project)
    path = root / "AGENTS.md"
    if path.is_symlink():
        raise ValueError("AGENTS.md cannot be a symbolic link")
    if path.exists() and (not path.is_file() or path.resolve().parent != root):
        raise ValueError("AGENTS.md must be a regular file in the project root")
    return path


def get_agent_config(project_id: int) -> dict[str, Any] | None:
    project = get_project(project_id)
    if project is None:
        return None
    path = _instructions_path(project)
    instructions = path.read_text(encoding="utf-8") if path.exists() else ""
    if len(instructions) > MAX_INSTRUCTIONS_CHARS:
        instructions = instructions[:MAX_INSTRUCTIONS_CHARS]
    skills = project.state.get("agent_skills", [])
    if not isinstance(skills, list):
        skills = []
    return {
        "project_id": project_id,
        "instruction_file": "AGENTS.md",
        "instructions": instructions,
        "skills": skills[:MAX_SKILLS],
        "limits": {
            "instructions_chars": MAX_INSTRUCTIONS_CHARS,
            "skills": MAX_SKILLS,
            "skill_content_chars": MAX_SKILL_CONTENT_CHARS,
            "enabled_skill_total_chars": MAX_ENABLED_SKILL_TOTAL_CHARS,
        },
    }


def save_agent_config(
    project_id: int, *, instructions: str, skills: list[dict[str, Any]],
) -> dict[str, Any] | None:
    project = get_project(project_id)
    if project is None:
        return None
    if not isinstance(instructions, str) or len(instructions) > MAX_INSTRUCTIONS_CHARS:
        raise ValueError(f"instructions must be text up to {MAX_INSTRUCTIONS_CHARS} characters")
    if len(skills) > MAX_SKILLS:
        raise ValueError(f"at most {MAX_SKILLS} skills are allowed")

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in skills:
        if not isinstance(item, dict):
            raise ValueError("Each skill must be an object")
        name = str(item.get("name", "")).strip()
        content = item.get("content", "")
        enabled = item.get("enabled", True)
        if not name or len(name) > MAX_SKILL_NAME_CHARS:
            raise ValueError(f"Skill name must contain 1-{MAX_SKILL_NAME_CHARS} characters")
        if name.casefold() in seen:
            raise ValueError("Skill names must be unique")
        if not isinstance(content, str) or len(content) > MAX_SKILL_CONTENT_CHARS:
            raise ValueError(f"Skill content must be text up to {MAX_SKILL_CONTENT_CHARS} characters")
        if not isinstance(enabled, bool):
            raise ValueError("Skill enabled must be boolean")
        seen.add(name.casefold())
        normalized.append({"name": name, "content": content, "enabled": enabled})

    enabled_total = sum(len(item["content"]) for item in normalized if item["enabled"])
    if enabled_total > MAX_ENABLED_SKILL_TOTAL_CHARS:
        raise ValueError(f"Enabled skill content must total at most {MAX_ENABLED_SKILL_TOTAL_CHARS} characters")

    path = _instructions_path(project)
    if instructions:
        path.write_text(instructions, encoding="utf-8")
    elif path.exists():
        path.unlink()

    state = dict(project.state)
    state["agent_skills"] = normalized
    updated = update_project(project_id, state=state)
    if updated is None:
        return None
    return get_agent_config(project_id)
