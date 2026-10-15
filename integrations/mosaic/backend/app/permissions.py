from app.models.action import Action
from app.models.action_repository import update_action
from app.core.state_transitions import ACTION_TRANSITIONS, validate_transition


def transition_action(action: Action, status: str, result: dict | None = None) -> Action:
    validate_transition("action", action.status, status, ACTION_TRANSITIONS)

    return update_action(action.id, status=status, result=result)


def approve_action(action: Action) -> Action:
    return transition_action(action, "approved")


def reject_action(action: Action) -> Action:
    return transition_action(action, "rejected")


def begin_action(action: Action) -> Action:
    return transition_action(action, "executing")


def complete_action(action: Action, result: dict) -> Action:
    return transition_action(action, "completed", result=result)


def fail_action(action: Action, result: dict | None = None) -> Action:
    return transition_action(action, "failed", result=result)


def cancel_action(action: Action) -> Action:
    return transition_action(action, "cancelled")
