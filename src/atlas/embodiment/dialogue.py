"""Memory-aware responder with explicit optional persistence adapter."""
from __future__ import annotations

class DialogueCoordinator:
    def __init__(self, responder, memory=None): self.responder=responder;self.memory=memory

    def reply(self,text,history):
        context=list(history)
        if self.memory is not None:
            extra=self.memory.recall(text)
            if extra: context=[("context",str(extra)),*context]
        answer=self.responder.reply(text,context)
        if not isinstance(answer,str) or not answer.strip(): raise ValueError("empty response")
        if self.memory is not None: self.memory.remember(text,answer)
        return answer


class BoundedDialogue:
    """Per-session history; callers supply an explicit session ID."""
    def __init__(self, coordinator: DialogueCoordinator, *, max_turns: int = 6):
        if max_turns < 1:
            raise ValueError("max_turns must be positive")
        self.coordinator = coordinator
        self.max_turns = max_turns
        self.sessions: dict[str, list[tuple[str, str]]] = {}

    def reply(self, session_id: str, text: str) -> str:
        if not session_id or not isinstance(text, str) or not text.strip():
            raise ValueError("session and text required")
        history = self.sessions.get(session_id, [])
        answer = self.coordinator.reply(text, list(history))
        self.sessions[session_id] = (history + [(text, answer)])[-self.max_turns:]
        return answer
