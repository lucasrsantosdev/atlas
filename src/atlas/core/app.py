from __future__ import annotations

from dataclasses import dataclass

from atlas.core.config import AtlasConfig
from atlas.core.registry import ComponentRegistry
from atlas.core.status import ComponentState, SystemState
from atlas.identity import AtlasIdentity


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

    Responsabilidades atuais:
    - receber configuração validada;
    - receber identidade validada;
    - registrar componentes;
    - calcular saúde do sistema;
    - fornecer estado geral do núcleo.

    Componentes ainda não implementados:
    - runtime local;
    - modelo de IA;
    - memória persistente;
    - RAG;
    - ferramentas.
    """

    def __init__(
        self,
        config: AtlasConfig,
        identity: AtlasIdentity,
    ) -> None:
        self.config = config
        self.identity = identity
        self.registry = ComponentRegistry()

        self._validate_identity_consistency()
        self._register_base_components()

        self.name = identity.name
        self.version = identity.version

    def _validate_identity_consistency(self) -> None:
        if self.config.atlas.name != self.identity.name:
            raise ValueError(
                "Nome da configuração e identidade são diferentes."
            )

        if self.config.atlas.version != self.identity.version:
            raise ValueError(
                "Versão da configuração e identidade são diferentes."
            )

    def _register_base_components(self) -> None:
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

        self.registry.register(
            "memory",
            ComponentState.DISABLED,
            critical=False,
            detail="Memória persistente ainda não implementada.",
        )

        self.registry.register(
            "knowledge",
            ComponentState.DISABLED,
            critical=False,
            detail="Conhecimento/RAG ainda não implementado.",
        )

        self.registry.register(
            "model_runtime",
            ComponentState.DISABLED,
            critical=False,
            detail="Runtime local ainda não implementado.",
        )

        self.registry.register(
            "model_router",
            ComponentState.DISABLED,
            critical=False,
            detail="Model Router ainda não implementado.",
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