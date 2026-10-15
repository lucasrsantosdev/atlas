from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.message import Message
from app.models.message_repository import create_message, list_messages


class MessageCreate(BaseModel):
    role: str
    content: str
    metadata: dict[str, Any] | None = None


router = APIRouter(prefix="/conversations/{conversation_id}/messages", tags=["messages"])


@router.post("", response_model=Message)
def create_message_endpoint(conversation_id: int, payload: MessageCreate) -> Message:
    try:
        return create_message(
            conversation_id=conversation_id,
            role=payload.role,
            content=payload.content,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[Message])
def list_messages_endpoint(conversation_id: int) -> list[Message]:
    try:
        return list_messages(conversation_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
