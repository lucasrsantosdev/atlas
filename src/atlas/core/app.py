from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from atlas.core.config import AtlasConfig
from atlas.core.registry import ComponentRegistry
from atlas.core.status import ComponentState, SystemState
from atlas.identity import (
    AtlasIdentity,
    build_identity_context,
)
from atlas.memory import (
    ConversationRole,
    MemoryRecord,
    MemoryService,
    MemorySource,
    MemoryType,
    MemoryVerification,
    SessionMemory,
)
from atlas.models.router import (
    ModelRouter,
    ModelRouterError,
)
from atlas.models.runtime import GenerationResult


@dataclass(frozen=True)
class AtlasStatus:
    name: str
    version: str
    startup_status: str
    system_state: SystemState
    offline_first: bool
    environment: str
    language: str
    identity_loaded: bool
    identity_type: str
    principles_loaded: int
    ready_components: int
    total_components: int


class Atlas:
    """
    Núcleo de coordenação do Atlas.
    """

    def __init__(
        self,
        config: AtlasConfig,
        identity: AtlasIdentity,
        model_router: ModelRouter | None = None,
        memory_service: MemoryService | None = None,
        session_memory: SessionMemory | None = None,
    ) -> None:
        self.config = config
        self.identity = identity
        self.model_router = model_router
        self.memory_service = memory_service
        self.session_memory = (
            session_memory
            if session_memory is not None
            else SessionMemory()
        )        
        self.registry = ComponentRegistry()

        self._validate_identity_consistency()

        self.name = identity.name
        self.version = identity.version

        self.identity_context = build_identity_context(
            identity
        )

        self._register_components()

    def _validate_identity_consistency(self) -> None:
        if self.config.atlas.name != self.identity.name:
            raise ValueError(
                "Nome da configuração e identidade são diferentes."
            )

        if self.config.atlas.version != self.identity.version:
            raise ValueError(
                "Versão da configuração e identidade são diferentes."
            )

    def _register_components(self) -> None:
        self.registry.register(
            "configuration",
            ComponentState.READY,
            critical=True,
            detail="Configuração carregada e validada.",
        )

        self.registry.register(
            "identity",
            ComponentState.READY,
            critical=True,
            detail="Identidade carregada e validada.",
        )

        if self.memory_service is None:
            self.registry.register(
                "memory",
                ComponentState.DISABLED,
                critical=False,
                detail="Memória persistente não configurada.",
            )
        else:
            self.registry.register(
                "memory",
                ComponentState.READY,
                critical=False,
                detail=(
                    "Memória persistente local disponível."
                ),
            )

        self.registry.register(
            "knowledge",
            ComponentState.DISABLED,
            critical=False,
            detail="Conhecimento/RAG ainda não implementado.",
        )

        if self.model_router is None:
            self.registry.register(
                "model_runtime",
                ComponentState.DISABLED,
                critical=False,
                detail="Nenhum runtime registrado.",
            )

            self.registry.register(
                "local_model",
                ComponentState.DISABLED,
                critical=False,
                detail="Nenhum modelo local registrado.",
            )

            self.registry.register(
                "model_router",
                ComponentState.DISABLED,
                critical=False,
                detail="Model Router não configurado.",
            )

            return

        router_status = self.model_router.status()

        if router_status.ready:
            self.registry.register(
                "model_runtime",
                ComponentState.READY,
                critical=False,
                detail="Runtime de modelo disponível.",
            )

            self.registry.register(
                "local_model",
                ComponentState.READY,
                critical=False,
                detail=(
                    "Rotas disponíveis: "
                    + ", ".join(router_status.available_roles)
                    + "."
                ),
            )

            self.registry.register(
                "model_router",
                ComponentState.READY,
                critical=False,
                detail=router_status.detail,
            )

        else:
            self.registry.register(
                "model_runtime",
                ComponentState.UNAVAILABLE,
                critical=False,
                detail="Runtime de modelo indisponível.",
            )

            self.registry.register(
                "local_model",
                ComponentState.UNAVAILABLE,
                critical=False,
                detail="Modelo local indisponível.",
            )

            self.registry.register(
                "model_router",
                ComponentState.UNAVAILABLE,
                critical=False,
                detail=router_status.detail,
            )

    def start(self) -> AtlasStatus:
        system_status = self.registry.system_status()

        return AtlasStatus(
            name=self.name,
            version=self.version,
            startup_status=self.config.system.startup_status,
            system_state=system_status.state,
            offline_first=self.config.runtime.offline_first,
            environment=self.config.runtime.environment,
            language=self.config.runtime.language,
            identity_loaded=True,
            identity_type=self.identity.agent_type,
            principles_loaded=len(self.identity.principles),
            ready_components=system_status.ready_components,
            total_components=system_status.total_components,
        )

    def remember(
        self,
        *,
        memory_type: MemoryType,
        content: str,
        source: MemorySource,
        explicit_user_authorization: bool = False,
        system_owned: bool = False,
        verification: MemoryVerification = MemoryVerification.UNVERIFIED,
        confidence: float = 1.0,
        tags: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        if self.memory_service is None:
            raise RuntimeError(
                "Serviço de memória não configurado."
            )

        return self.memory_service.remember(
            memory_type=memory_type,
            content=content,
            source=source,
            explicit_user_authorization=(
                explicit_user_authorization
            ),
            system_owned=system_owned,
            verification=verification,
            confidence=confidence,
            tags=tags,
            metadata=metadata,
        )

    def recall_by_id(
        self,
        memory_id: str,
    ) -> MemoryRecord | None:
        if self.memory_service is None:
            raise RuntimeError(
                "Serviço de memória não configurado."
            )

        return self.memory_service.recall_by_id(
            memory_id
        )

    def recall_text(
        self,
        query: str,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        if self.memory_service is None:
            raise RuntimeError(
                "Serviço de memória não configurado."
            )

        return self.memory_service.recall_text(
            query,
            memory_type=memory_type,
            limit=limit,
        )

    def recall_recent(
        self,
        *,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> tuple[MemoryRecord, ...]:
        if self.memory_service is None:
            raise RuntimeError(
                "Serviço de memória não configurado."
            )

        return self.memory_service.recall_recent(
            memory_type=memory_type,
            limit=limit,
        )


    def _build_session_prompt(
        self,
        user_message: str,
    ) -> str:
        """
        Constrói o contexto temporário da conversa atual.

        Este contexto existe somente em RAM e não representa
        memória persistente do Atlas.
        """

        lines = [
            "Contexto temporário da conversa atual:",
            "",
        ]

        for turn in self.session_memory.all():
            if turn.role == ConversationRole.USER:
                speaker = "Usuário"
            elif turn.role == ConversationRole.ASSISTANT:
                speaker = "Atlas"
            else:
                speaker = "Sistema"

            lines.append(
                f"{speaker}: {turn.content}"
            )

        lines.extend(
            [
                f"Usuário: {user_message}",
                "",
                "Instruções sobre este contexto:",
                (
                    "- Use os turnos anteriores somente para manter "
                    "continuidade nesta conversa."
                ),
                (
                    "- Não trate este histórico temporário como "
                    "memória persistente."
                ),
                (
                    "- Não invente informações que não estejam "
                    "presentes no contexto."
                ),
                "- Responda à última mensagem do usuário.",
            ]
        )

        return "\n".join(lines)

    def process_message(
        self,
        message: str,
        *,
        role: str = "primary",
    ) -> GenerationResult:
        """
        Processa uma mensagem usando memória curta da sessão.

        A conversa é mantida somente em RAM.
        """

        clean_message = message.strip()

        if not clean_message:
            raise ValueError(
                "Mensagem não pode estar vazia."
            )

        prompt = self._build_session_prompt(
            clean_message
        )

        result = self.generate(
            prompt,
            role=role,
        )

        self.session_memory.add(
            role=ConversationRole.USER,
            content=clean_message,
        )

        self.session_memory.add(
            role=ConversationRole.ASSISTANT,
            content=result.response,
        )

        return result

    def generate(
        self,
        prompt: str,
        *,
        role: str = "primary",
    ) -> GenerationResult:
        if self.model_router is None:
            raise ModelRouterError(
                "Model Router não configurado."
            )

        return self.model_router.generate(
            prompt,
            role=role,
            system_prompt=self.identity_context,
        )
