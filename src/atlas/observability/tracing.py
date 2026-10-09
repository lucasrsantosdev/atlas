"""Trilha de auditoria mínima, em memória, sem armazenar entradas pessoais."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    event: str
    status: str
    detail: str = ""

class AuditTrail:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: str, status: str, detail: str = "") -> AuditEvent:
        item = AuditEvent(datetime.now(timezone.utc).isoformat(), event, status, detail)
        self._events.append(item)
        return item

    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)
