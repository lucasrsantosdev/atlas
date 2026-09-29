from __future__ import annotations

from dataclasses import dataclass

from atlas.core.config import AtlasConfig
from atlas.core.registry import ComponentRegistry
from atlas.core.status import ComponentState, SystemState
from atlas.identity import AtlasIdentity
from atlas.models.runtime import (
    GenerationResult,
    ModelRuntime,
    ModelRuntimeError,
)


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
    - monitorar saúde do sistema;
    - utilizar um runtime cognitivo local;
    - executar um modelo local.

    Ainda não implementado:
    - Model Router;
    - memória persistente;
    - Knowledge/RAG;
    - ferramentas;
    - interfaces avançadas.
    """

    def __init__(
        self,
        config: AtlasConfig,
        identity: AtlasIdentity,
        runtime: ModelRuntime | None = None,
        model_name: str | None = None,
    ) -> None:
        self.config = config
        self.identity = identity
        self.runtime = runtime
        self.model_name = model_name
        self.registry = ComponentRegistry()

        self._validate_identity_consistency()

        self.name = identity.name
        self.version = identity.version

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

        if self.runtime is None:
            self.registry.register(
                "model_runtime",
                ComponentState.DISABLED,
                critical=False,
                detail="Runtime local não configurado.",
            )

            self.registry.register(
                "local_model",
                ComponentState.DISABLED,
                critical=False,
                detail="Modelo local não configurado.",
            )

        else:
            runtime_health = self.runtime.health()

            self.registry.register(
                "model_runtime",
                (
                    ComponentState.READY
                    if runtime_health.available
                    else ComponentState.UNAVAILABLE
                ),
                critical=False,
                detail=runtime_health.detail,
            )

            if runtime_health.available and self.model_name:
                self.registry.register(
                    "local_model",
                    ComponentState.READY,
                    critical=False,
                    detail=f"Modelo configurado: {self.model_name}.",
                )
            else:
                self.registry.register(
                    "local_model",
                    ComponentState.UNAVAILABLE,
                    critical=False,
                    detail="Modelo local indisponível.",
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

    def generate(self, prompt: str) -> GenerationResult:
        if self.runtime is None:
            raise ModelRuntimeError(
                "Nenhum runtime cognitivo foi configurado."
            )

        if not self.model_name:
            raise ModelRuntimeError(
                "Nenhum modelo local foi configurado."
            )

        return self.runtime.generate(
            model=self.model_name,
            prompt=prompt,
        )
