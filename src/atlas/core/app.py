from __future__ import annotations

from dataclasses import dataclass

from atlas.core.config import AtlasConfig
from atlas.identity import AtlasIdentity


@dataclass(frozen=True)
class AtlasStatus:
    name: str
    version: str
    status: str
    offline_first: bool
    environment: str
    language: str
    identity_loaded: bool
    identity_type: str
    principles_loaded: int


class Atlas:
    """
    Núcleo inicial do Atlas.

    Responsabilidades atuais:
    - receber configuração validada;
    - receber identidade validada;
    - manter estado básico;
    - inicializar o núcleo.

    Componentes ainda não implementados:
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

        if config.atlas.name != identity.name:
            raise ValueError(
                "Nome da configuração e identidade são diferentes."
            )

        if config.atlas.version != identity.version:
            raise ValueError(
                "Versão da configuração e identidade são diferentes."
            )

        self.name = identity.name
        self.version = identity.version

    def start(self) -> AtlasStatus:
        return AtlasStatus(
            name=self.name,
            version=self.version,
            status=self.config.system.startup_status,
            offline_first=self.config.runtime.offline_first,
            environment=self.config.runtime.environment,
            language=self.config.runtime.language,
            identity_loaded=True,
            identity_type=self.identity.agent_type,
            principles_loaded=len(self.identity.principles),
        )