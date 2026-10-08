from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Permission(str, Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"

    NETWORK = "network"

    EXECUTE_PROCESS = "execute_process"

    DATABASE_READ = "database_read"
    DATABASE_WRITE = "database_write"

    GIT_READ = "git_read"
    GIT_WRITE = "git_write"

    HARDWARE_READ = "hardware_read"
    HARDWARE_WRITE = "hardware_write"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    risk: RiskLevel
    requires_confirmation: bool
    reason: str


class PolicyEngine:
    """
    Motor de políticas do Atlas.

    Decide se uma capacidade pode ser utilizada
    antes que uma ferramenta execute qualquer ação.
    """

    def __init__(
        self,
        allowed: set[Permission] | None = None,
    ) -> None:
        self.allowed = set(
            allowed or ()
        )

    def evaluate(
        self,
        permission: Permission,
        risk: RiskLevel = RiskLevel.LOW,
    ) -> PolicyDecision:

        permitted = permission in self.allowed

        requires_confirmation = (
            permitted
            and risk
            in {
                RiskLevel.HIGH,
                RiskLevel.CRITICAL,
            }
        )

        if permitted:
            reason = "permission granted"
        else:
            reason = "permission denied"

        return PolicyDecision(
            allowed=permitted,
            risk=risk,
            requires_confirmation=requires_confirmation,
            reason=reason,
        )
