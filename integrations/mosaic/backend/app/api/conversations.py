from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.conversation import Conversation
from app.models.conversation_repository import (
    create_conversation,
    get_conversation,
    list_conversations,
    update_conversation,
)


class ConversationCreate(BaseModel):
    title: str
    model_id: int
    project_id: int | None = None


class ConversationUpdate(BaseModel):
    title: str | None = None
    model_id: int | None = None
    project_id: int | None = None


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=Conversation)
def create_conversation_endpoint(payload: ConversationCreate) -> Conversation:
    try:
        return create_conversation(
            title=payload.title,
            model_id=payload.model_id,
            project_id=payload.project_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[Conversation])
def list_conversations_endpoint() -> list[Conversation]:
    return list_conversations()


@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation_endpoint(conversation_id: int) -> Conversation:
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.patch("/{conversation_id}", response_model=Conversation)
def update_conversation_endpoint(
    conversation_id: int,
    payload: ConversationUpdate,
) -> Conversation:
    conversation = update_conversation(
        conversation_id,
        title=payload.title,
        model_id=payload.model_id,
        project_id=payload.project_id,
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
