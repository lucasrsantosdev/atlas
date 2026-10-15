from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.action import Action
from app.models.action_repository import (
    create_action,
    delete_action,
    get_action,
    list_actions,
)
from app.permissions import (
    approve_action,
    begin_action,
    cancel_action,
    complete_action,
    fail_action,
    reject_action,
)


class ActionCreate(BaseModel):
    task_id: int
    type: str
    target: str | None = None
    payload: dict[str, Any] = {}
    status: str = "pending"
    result: dict[str, Any] | None = None


class ActionResult(BaseModel):
    result: dict[str, Any] | None = None


router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("", response_model=Action)
def create_action_endpoint(payload: ActionCreate) -> Action:
    try:
        return create_action(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[Action])
def list_actions_endpoint(task_id: int | None = None) -> list[Action]:
    return list_actions(task_id)


@router.get("/{action_id}", response_model=Action)
def get_action_endpoint(action_id: int) -> Action:
    action = get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


def _transition(action_id: int, operation) -> Action:
    action = get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    try:
        return operation(action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{action_id}/approve", response_model=Action)
def approve_action_endpoint(action_id: int) -> Action:
    return _transition(action_id, approve_action)


@router.post("/{action_id}/reject", response_model=Action)
def reject_action_endpoint(action_id: int) -> Action:
    return _transition(action_id, reject_action)


@router.post("/{action_id}/execute", response_model=Action)
def execute_action_endpoint(action_id: int) -> Action:
    return _transition(action_id, begin_action)


@router.post("/{action_id}/complete", response_model=Action)
def complete_action_endpoint(action_id: int, payload: ActionResult) -> Action:
    return _transition(
        action_id,
        lambda action: complete_action(action, payload.result or {}),
    )


@router.post("/{action_id}/fail", response_model=Action)
def fail_action_endpoint(action_id: int, payload: ActionResult) -> Action:
    return _transition(
        action_id,
        lambda action: fail_action(action, payload.result),
    )


@router.post("/{action_id}/cancel", response_model=Action)
def cancel_action_endpoint(action_id: int) -> Action:
    return _transition(action_id, cancel_action)


@router.delete("/{action_id}")
def delete_action_endpoint(action_id: int) -> dict[str, bool]:
    if not delete_action(action_id):
        raise HTTPException(status_code=404, detail="Action not found")
    return {"deleted": True}
