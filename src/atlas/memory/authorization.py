from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from atlas.memory.models import (
    MemorySource,
    MemoryType,
)


class MemoryAuthorizationError(RuntimeError):
    """Tentativa de persistência sem autorização válida."""


class AuthorizationReason(str, Enum):
    EXPLICIT_USER = "explicit_user"
    SYSTEM_HISTORY = "system_history"
    DENIED_BY_DEFAULT = "denied_by_default"


@dataclass(frozen=True)
class MemoryAuthorizationDecision:
    allowed: bool
    reason: AuthorizationReason
    detail: str


class MemoryAuthorizationPolicy:
    """
    Política inicial de autorização da memória Atlas.

    Princípio:
    memória permanente é opt-in por padrão.

    Exceção:
    eventos internos pertencentes à própria história
    operacional do Atlas podem ser registrados em
    categorias restritas.
    """

    SYSTEM_HISTORY_TYPES = frozenset(
        {
            MemoryType.TIMELINE,
            MemoryType.DECISIONS,
            MemoryType.ARCHIVE,
        }
    )

    def evaluate(
        self,
        *,
        memory_type: MemoryType,
        source: MemorySource,
        explicit_user_authorization: bool = False,
        system_owned: bool = False,
    ) -> MemoryAuthorizationDecision:

        if explicit_user_authorization:
            return MemoryAuthorizationDecision(
                allowed=True,
                reason=AuthorizationReason.EXPLICIT_USER,
                detail=(
                    "Persistência autorizada explicitamente "
                    "pelo usuário."
                ),
            )

        if (
            source == MemorySource.SYSTEM
            and system_owned
            and memory_type in self.SYSTEM_HISTORY_TYPES
        ):
            return MemoryAuthorizationDecision(
                allowed=True,
                reason=AuthorizationReason.SYSTEM_HISTORY,
                detail=(
                    "Evento interno autorizado como parte "
                    "da história operacional do Atlas."
                ),
            )

        return MemoryAuthorizationDecision(
            allowed=False,
            reason=AuthorizationReason.DENIED_BY_DEFAULT,
            detail=(
                "Persistência negada por padrão. "
                "É necessária autorização explícita."
            ),
        )
