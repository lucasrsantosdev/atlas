import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.message import Message
from app.services.chat import chat, stream_chat


class ChatRequest(BaseModel):
    content: str


router = APIRouter(prefix="/conversations/{conversation_id}/chat", tags=["chat"])


@router.post("", response_model=Message)
def chat_endpoint(conversation_id: int, payload: ChatRequest) -> Message:
    try:
        return chat(conversation_id, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/stream")
def stream_chat_endpoint(conversation_id: int, payload: ChatRequest):
    try:
        stream = stream_chat(conversation_id, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    def events():
        try:
            for chunk in stream:
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except RuntimeError as exc:
            yield f"event: error\ndata: {json.dumps(str(exc), ensure_ascii=False)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
