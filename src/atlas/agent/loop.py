"""Agent Loop v0: análise seguida de passos explicitamente fornecidos.

NÃO infere execução a partir de texto livre nem autoriza ações por conta própria.
O ToolRegistry existente continua sendo o responsável pela política.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from atlas.mosaic.models import MosaicRequest, MosaicResult
from atlas.mosaic.service import MosaicService
from atlas.tools.registry import ToolRegistry, ToolResult
from atlas.observability import AuditTrail

@dataclass(frozen=True)
class PlannedToolCall:
    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    confirmed: bool = False

@dataclass(frozen=True)
class AgentOutcome:
    analysis: MosaicResult
    results: tuple[ToolResult, ...]
    stopped_reason: str

class AgentLoop:
    def __init__(self, mosaic: MosaicService, tools: ToolRegistry,
                 audit: AuditTrail | None = None, max_steps: int = 5) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be >= 1")
        self.mosaic = mosaic
        self.tools = tools
        self.audit = audit if audit is not None else AuditTrail()
        self.max_steps = max_steps

    def run(self, request: MosaicRequest,
            steps: tuple[PlannedToolCall, ...] = ()) -> AgentOutcome:
        analysis = self.mosaic.analyze(request)
        self.audit.record("mosaic.analyze", "ok", analysis.intent.value)
        if not steps:
            return AgentOutcome(analysis, (), "analysis_only")
        if len(steps) > self.max_steps:
            self.audit.record("agent.limit", "blocked", "max_steps")
            return AgentOutcome(analysis, (), "max_steps_exceeded")
        results: list[ToolResult] = []
        for step in steps:
            # Explicit tool plan is not the same as an authorization.
            try:
                result = self.tools.execute(step.tool_name,
                                            confirmed=step.confirmed,
                                            **step.arguments)
            except Exception as exc:
                # Avoid storing raw argument contents or exception text.
                self.audit.record("tool.execute", "error", step.tool_name)
                return AgentOutcome(analysis, tuple(results), "tool_error")
            results.append(result)
            self.audit.record("tool.execute", "ok" if result.success else "blocked_or_failed",
                              step.tool_name)
            if not result.success:
                return AgentOutcome(analysis, tuple(results), "tool_failed_or_denied")
        return AgentOutcome(analysis, tuple(results), "completed")
