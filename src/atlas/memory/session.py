from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class ConversationRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ConversationTurn:
    role: ConversationRole
    content: str
    created_at: str

    @classmethod
    def create(
        cls,
        *,
        role: ConversationRole,
        content: str,
    ) -> "ConversationTurn":
        clean_content = content.strip()

        if not clean_content:
            raise ValueError(
                "Conteúdo da conversa não pode estar vazio."
            )

        return cls(
            role=role,
            content=clean_content,
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )


class SessionMemory:
    """
    Memória conversacional temporária do Atlas.

    Existe somente durante a execução atual.

    Não persiste em disco.
    """

    def __init__(
        self,
        *,
        max_turns: int = 20,
    ) -> None:
        if max_turns <= 0:
            raise ValueError(
                "max_turns deve ser maior que zero."
            )

        self.max_turns = max_turns
        self._turns: list[ConversationTurn] = []

    def add(
        self,
        *,
        role: ConversationRole,
        content: str,
    ) -> ConversationTurn:
        turn = ConversationTurn.create(
            role=role,
            content=content,
        )

        self._turns.append(turn)

        if len(self._turns) > self.max_turns:
            self._turns = self._turns[
                -self.max_turns:
            ]

        return turn

    def all(
        self,
    ) -> tuple[ConversationTurn, ...]:
        return tuple(self._turns)

    def clear(self) -> None:
        self._turns.clear()

    def __len__(self) -> int:
        return len(self._turns)
