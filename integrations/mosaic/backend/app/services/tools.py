import json
from pathlib import Path
from typing import Any

from app.core.config import DATA_DIR
from app.models.conversation_repository import get_conversation
from app.models.project_repository import get_project
from app.models.task_repository import get_task
from app.models.tool_call import ToolCall
from app.models.tool_call_repository import get_tool_call, update_tool_call
from app.models.tool_result import ToolResult
from app.models.tool_result_repository import create_tool_result
from app.tools import registry


def resolve_tool_workspace(tool_call: ToolCall) -> Path:
    """Resolve the active task/project workspace; never trust a model-supplied root."""
    workspace = None
    if tool_call.task_id is not None:
        task = get_task(tool_call.task_id)
        if task is None:
            raise ValueError("ToolCall references a missing task")
        task_conversation = get_conversation(task.conversation_id) if task.conversation_id is not None else None
        call_conversation = get_conversation(tool_call.conversation_id)
        if task.conversation_id is not None and task.conversation_id != tool_call.conversation_id:
            raise ValueError("ToolCall conversation does not match its task")
        if task_conversation is not None and call_conversation is not None:
            if task_conversation.project_id != call_conversation.project_id and task.project_id is None:
                raise ValueError("ToolCall project scope does not match its conversation")
        if task.project_id is not None:
            if call_conversation is not None and call_conversation.project_id not in {None, task.project_id}:
                raise ValueError("ToolCall project scope does not match its task")
            project = get_project(task.project_id)
            if project is None:
                raise ValueError("Task references a missing project")
            workspace = project.workspace
        elif task_conversation is not None and task_conversation.project_id is not None:
            project = get_project(task_conversation.project_id)
            if project is None:
                raise ValueError("Conversation references a missing project")
            workspace = project.workspace
    else:
        conversation = get_conversation(tool_call.conversation_id)
        if conversation is not None and conversation.project_id is not None:
            project = get_project(conversation.project_id)
            if project is None:
                raise ValueError("Conversation references a missing project")
            workspace = project.workspace
    if workspace is None:
        workspace = str(DATA_DIR / "workspaces" / "default")
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve(strict=True)


def resolve_tool_policy(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """The Core's single policy decision point for a proposed tool operation."""
    tool = registry.get(tool_name)
    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    tool.validate(arguments)
    policy = tool.permission_policy
    approval_required = policy.get("approval_required")
    if not isinstance(approval_required, bool):
        raise ValueError(f"Tool {tool_name} has no valid approval policy")
    return {
        "tool_name": tool_name,
        "approval_required": approval_required,
        "scope": policy.get("scope", "none"),
        "timeout_seconds": policy.get("timeout_seconds"),
    }


def validate_tool_call(tool_call: ToolCall) -> None:
    resolve_tool_policy(tool_call.tool_name, tool_call.arguments)


def approve_tool_call(tool_call: ToolCall) -> ToolCall:
    if tool_call.status != "pending":
        raise ValueError(f"Invalid tool call transition: {tool_call.status} -> approved")
    validate_tool_call(tool_call)
    updated = update_tool_call(tool_call.id, status="approved")
    if updated is None:
        raise ValueError("ToolCall no longer exists")
    return updated


def execute_tool_call(tool_call: ToolCall) -> ToolResult:
    # Re-fetch at the execution boundary so stale caller state cannot authorize execution.
    current = get_tool_call(tool_call.id)
    if current is None:
        raise ValueError("ToolCall not found")
    if current.status != "approved":
        raise ValueError("Tool call must be approved before execution")
    tool = registry.get(current.tool_name)
    if tool is None:
        update_tool_call(current.id, status="failed")
        return create_tool_result(current.id, "failed", error=f"Unknown tool: {current.tool_name}")
    try:
        tool.validate(current.arguments)
    except Exception as exc:
        update_tool_call(current.id, status="failed")
        return create_tool_result(current.id, "failed", error=f"{type(exc).__name__}: {exc}")

    executing = update_tool_call(current.id, status="executing")
    if executing is None:
        raise ValueError("ToolCall no longer exists")
    try:
        workspace = resolve_tool_workspace(executing) if executing.tool_name in {"filesystem", "terminal"} else None
        def is_cancelled() -> bool:
            if executing.task_id is None:
                return False
            task = get_task(executing.task_id)
            return task is None or task.status == "cancelled"

        data = tool.execute(
            executing.arguments,
            workspace=workspace,
            cancel_check=is_cancelled if executing.tool_name == "terminal" else None,
        )
    except Exception as exc:
        update_tool_call(executing.id, status="failed")
        return create_tool_result(executing.id, "failed", error=f"{type(exc).__name__}: {exc}")

    if isinstance(data, dict) and data.get("status") in {"timeout", "cancelled", "launch_failure"}:
        call_status = "cancelled" if data["status"] == "cancelled" else "failed"
        update_tool_call(executing.id, status=call_status)
        return create_tool_result(
            executing.id,
            "failed",
            error=json.dumps(data, ensure_ascii=False),
        )

    update_tool_call(executing.id, status="completed")
    if not isinstance(data, dict):
        data = {"value": data}
    return create_tool_result(executing.id, "completed", data=data)
