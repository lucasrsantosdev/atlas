import asyncio
import json
import time
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict

from app.models.conversation_repository import get_conversation
from app.models.message_repository import create_message
from app.models.task import Task
from app.models.task_event import TaskEvent
from app.models.task_event_repository import list_task_events
from app.services.agent import run_agent
from app.services.tools import approve_tool_call, execute_tool_call
from app.models.tool_call_repository import get_tool_call, update_tool_call
from app.services.agent_decision import create_provider_decider
from app.models.task_repository import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    update_task,
)


class TaskCreate(BaseModel):
    type: str
    mode: str
    conversation_id: int | None = None
    project_id: int | None = None
    status: str = "pending"
    plan: dict[str, Any] | None = None
    result: dict[str, Any] | None = None


class TaskStart(BaseModel):
    conversation_id: int
    goal: str
    type: str = "generic"


class ToolDecision(BaseModel):
    decision: str


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: int | None = None
    project_id: int | None = None
    type: str | None = None
    mode: str | None = None
    plan: dict[str, Any] | None = None
    result: dict[str, Any] | None = None


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task)
def create_task_endpoint(payload: TaskCreate) -> Task:
    try:
        task = create_task(**payload.model_dump())
        return task
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[Task])
def list_tasks_endpoint() -> list[Task]:
    return list_tasks()


@router.get("/{task_id}/events", response_model=list[TaskEvent])
def list_task_events_endpoint(task_id: int, after_id: int = 0, limit: int = 100) -> list[TaskEvent]:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        return list_task_events(task_id, after_id=after_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{task_id}/events/stream")
async def stream_task_events_endpoint(
    task_id: int, request: Request, after_id: int = 0,
) -> StreamingResponse:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    last_event_id = request.headers.get("last-event-id")
    if last_event_id:
        try:
            after_id = max(after_id, int(last_event_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Last-Event-ID header")
    if after_id < 0:
        raise HTTPException(status_code=422, detail="after_id must be non-negative")

    async def generate():
        cursor = after_id
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if await request.is_disconnected():
                break
            events = list_task_events(task_id, after_id=cursor, limit=100)
            if events:
                for event in events:
                    payload = json.dumps({
                        "id": event.id, "task_id": event.task_id,
                        "conversation_id": event.conversation_id, "project_id": event.project_id,
                        "tool_call_id": event.tool_call_id, "action_id": event.action_id,
                        "timestamp": event.timestamp, "level": event.level,
                        "component": event.component, "event_name": event.event_name,
                        "message": event.message, "duration_ms": event.duration_ms,
                        "status": event.status, "metadata": event.metadata,
                    }, ensure_ascii=False)
                    yield f"id: {event.id}\nevent: task_event\ndata: {payload}\n\n"
                    cursor = event.id
            else:
                yield ": keep-alive\n\n"
                await asyncio.sleep(1)

    return StreamingResponse(
        generate(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{task_id}", response_model=Task)
def get_task_endpoint(task_id: int) -> Task:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task_endpoint(task_id: int, payload: TaskUpdate) -> Task:
    try:
        task = update_task(task_id, **payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_task_endpoint(task_id: int) -> dict[str, bool]:
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}



@router.post("/{task_id}/cancel", response_model=Task)
def cancel_task_endpoint(task_id: int) -> Task:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        cancelled = update_task(task_id, status="cancelled")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if cancelled is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return cancelled



def _execute_approved_call_and_resume(task_id: int, tool_call_id: int) -> None:
    """Execute a pre-approved persisted ToolCall and resume the same Task."""
    try:
        current = get_task(task_id)
        call = get_tool_call(tool_call_id)
        if call is None or call.task_id != task_id or call.status != "approved":
            raise ValueError("Approved ToolCall is no longer available")
        if current is None or current.status == "cancelled":
            update_tool_call(tool_call_id, status="cancelled")
            return
        execute_tool_call(call)
        current = get_task(task_id)
        if current is None or current.status == "cancelled":
            return
        if current.status != "executing":
            return
        _run_provider_agent(task_id)
    except Exception as exc:
        current = get_task(task_id)
        if current is not None and current.status == "executing":
            try:
                update_task(task_id, status="failed", result={
                    "error": f"{type(exc).__name__}: {exc}",
                    "tool_call_id": tool_call_id,
                })
            except ValueError:
                pass


def _run_provider_agent(task_id: int) -> None:
    """Execute the persisted Task in the in-process background worker."""
    try:
        run_agent(task_id, create_provider_decider(task_id))
    except Exception as exc:
        current = get_task(task_id)
        if current is not None and current.status in {"pending", "executing"}:
            try:
                update_task(task_id, status="failed", result={"error": f"{type(exc).__name__}: {exc}"})
            except ValueError:
                # A concurrent cancellation or terminal transition remains authoritative.
                pass


@router.post("/start", response_model=Task, status_code=202)
def start_agent_task_endpoint(payload: TaskStart, background_tasks: BackgroundTasks) -> Task:
    """Persist the user's goal, create an agent Task, and start the provider-backed loop."""
    goal = payload.goal.strip()
    if not goal:
        raise HTTPException(status_code=422, detail="Task goal must not be empty")
    conversation = get_conversation(payload.conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if payload.type not in {"code_project", "document", "analysis", "report", "generic"}:
        raise HTTPException(status_code=422, detail="Invalid task type")
    # Persist the goal as a normal conversation message so it is part of the canonical context.
    create_message(conversation.id, "user", goal)
    try:
        task = create_task(
            type=payload.type,
            mode="agent",
            conversation_id=conversation.id,
            project_id=conversation.project_id,
            plan={"goal": goal},
        )
        claimed = update_task(task.id, status="executing")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if claimed is None:
        raise HTTPException(status_code=500, detail="Could not claim newly created Task")
    background_tasks.add_task(_run_provider_agent, task.id)
    return claimed


@router.post("/{task_id}/run", response_model=Task, status_code=202)
def run_task_endpoint(task_id: int, background_tasks: BackgroundTasks) -> Task:
    """Explicitly start an agent-mode Task; normal chat remains unchanged."""
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.mode != "agent":
        raise HTTPException(status_code=409, detail="Task must use agent mode")
    if task.conversation_id is None or get_conversation(task.conversation_id) is None:
        raise HTTPException(status_code=400, detail="Agent Task requires a valid conversation")
    if task.status != "pending":
        raise HTTPException(status_code=409, detail=f"Task cannot start from status: {task.status}")
    try:
        claimed = update_task(task_id, status="executing")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if claimed is None:
        raise HTTPException(status_code=404, detail="Task not found")
    background_tasks.add_task(_run_provider_agent, task_id)
    return claimed


@router.post("/{task_id}/tool-calls/{tool_call_id}/decision", response_model=Task, status_code=202)
def decide_tool_call_endpoint(
    task_id: int,
    tool_call_id: int,
    payload: ToolDecision,
    background_tasks: BackgroundTasks,
) -> Task:
    """Approve/reject the pending call, then resume the same persisted agent Task."""
    if payload.decision not in {"approve", "reject"}:
        raise HTTPException(status_code=422, detail="decision must be 'approve' or 'reject'")
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "awaiting_approval":
        raise HTTPException(status_code=409, detail="Task is not awaiting approval")
    call = get_tool_call(tool_call_id)
    if call is None or call.task_id != task_id:
        raise HTTPException(status_code=404, detail="Pending ToolCall not found for this Task")
    if call.status != "pending":
        raise HTTPException(status_code=409, detail=f"ToolCall is no longer pending: {call.status}")
    if payload.decision == "reject":
        try:
            update_tool_call(tool_call_id, status="rejected")
            updated = update_task(task_id, status="failed", result={
                "error": "A operação solicitada foi recusada pelo usuário.",
                "tool_call_id": tool_call_id,
            })
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated

    try:
        approve_tool_call(call)
        updated = update_task(task_id, status="executing", result={
            "last_tool_call_id": tool_call_id,
            "resuming": True,
        })
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    background_tasks.add_task(_execute_approved_call_and_resume, task_id, tool_call_id)
    return updated
