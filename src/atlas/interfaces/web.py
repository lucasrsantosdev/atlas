"""Interface HTTP do ATLAS.IA; utiliza exclusivamente o Core oficial."""

from threading import RLock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from atlas.__main__ import build_atlas

app = FastAPI(title="ATLAS.IA", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

lock = RLock()
atlas_instance = None
conversations = {}
active_conversation_id = None


def get_atlas():
    global atlas_instance
    with lock:
        if atlas_instance is None:
            atlas_instance = build_atlas()
        return atlas_instance


class ConversationCreate(BaseModel):
    project_id: str | int | None = None
    title: str | None = None


class ChatMessage(BaseModel):
    content: str


@app.get("/")
def root():
    return {"name": "ATLAS.IA", "status": "online", "core": "official"}


@app.get("/health")
def health():
    atlas = get_atlas()
    return {
        "name": atlas.identity.name,
        "version": atlas.identity.version,
        "status": "ready",
        "core": "atlas.core.app.Atlas",
    }


@app.get("/models")
def models():
    return [{"id": "primary", "name": "Atlas — Ollama", "provider": "ollama"}]


@app.get("/models/status")
def models_status():
    return {"status": "configured", "provider": "ollama"}


@app.get("/projects")
def projects():
    return [{
        "id": "atlas",
        "name": "ATLAS.IA",
        "description": "Projeto oficial de inteligencia artificial brasileira",
    }]


@app.get("/projects/{project_id}")
def project(project_id: str):
    if project_id != "atlas":
        raise HTTPException(404, "Projeto nao encontrado")
    return projects()[0]


@app.get("/conversations")
def list_conversations():
    with lock:
        return list(conversations.values())


@app.post("/conversations")
def create_conversation(payload: ConversationCreate):
    global active_conversation_id
    with lock:
        cid = str(uuid4())
        conversation = {
            "id": cid,
            "project_id": payload.project_id or "atlas",
            "title": payload.title or "Nova conversa",
            "messages": [],
        }
        conversations[cid] = conversation
        return conversation


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    with lock:
        conversation = conversations.get(conversation_id)
        if conversation is None:
            raise HTTPException(404, "Conversa nao encontrada")
        return conversation


@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: str):
    return get_conversation(conversation_id)["messages"]


@app.post("/conversations/{conversation_id}/chat")
def chat(conversation_id: str, payload: ChatMessage):
    global active_conversation_id

    message = payload.content.strip()
    if not message:
        raise HTTPException(400, "Mensagem vazia")

    with lock:
        if conversation_id not in conversations:
            raise HTTPException(404, "Conversa nao encontrada")

        if active_conversation_id not in (None, conversation_id):
            raise HTTPException(
                409,
                "Nesta primeira versao, apenas uma conversa pode utilizar "
                "a memoria curta do Atlas por vez. Reinicie a API para "
                "iniciar uma nova sessao.",
            )

        active_conversation_id = conversation_id

        # Mesma funcao utilizada pelo Atlas Core oficial.
        atlas = get_atlas()
        result = atlas.process_message(message)

        response = result.response

        user_message = {
            "id": str(uuid4()),
            "role": "user",
            "content": message,
        }

        assistant_message = {
            "id": str(uuid4()),
            "role": "assistant",
            "content": response,
        }

        conversations[conversation_id]["messages"].extend(
            [user_message, assistant_message]
        )

        return assistant_message
