from fastapi import APIRouter, HTTPException

from app.models.tool_call_repository import get_tool_call, list_tool_calls
from app.models.tool_result_repository import list_tool_results

router = APIRouter(prefix="/tool-calls", tags=["tool-calls"])


@router.get("")
def list_tool_calls_endpoint(conversation_id: int, task_id: int | None = None) -> list[dict]:
    calls = list_tool_calls(conversation_id)
    if task_id is not None:
        calls = [call for call in calls if call.task_id == task_id]
    return [
        {
            "id": call.id,
            "conversation_id": call.conversation_id,
            "task_id": call.task_id,
            "tool_name": call.tool_name,
            "arguments": call.arguments,
            "status": call.status,
            "created_at": call.created_at,
            "updated_at": call.updated_at,
            "results": [
                {
                    "id": result.id,
                    "tool_call_id": result.tool_call_id,
                    "status": result.status,
                    "data": result.data,
                    "error": result.error,
                    "created_at": result.created_at,
                }
                for result in list_tool_results(call.id)
            ],
        }
        for call in calls
    ]


@router.get("/{tool_call_id}")
def get_tool_call_endpoint(tool_call_id: int) -> dict:
    call = get_tool_call(tool_call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="ToolCall not found")
    return {
        "id": call.id,
        "conversation_id": call.conversation_id,
        "task_id": call.task_id,
        "tool_name": call.tool_name,
        "arguments": call.arguments,
        "status": call.status,
        "created_at": call.created_at,
        "updated_at": call.updated_at,
        "results": [
            {
                "id": result.id,
                "tool_call_id": result.tool_call_id,
                "status": result.status,
                "data": result.data,
                "error": result.error,
                "created_at": result.created_at,
            }
            for result in list_tool_results(call.id)
        ],
    }
