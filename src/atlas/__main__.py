from __future__ import annotations

import sys

from atlas.core import Atlas, AtlasConfigError, load_config
from atlas.identity import AtlasIdentityError, load_identity
from atlas.models import ModelConfigError, load_models_config
from atlas.models.runtime import OllamaRuntime


def main() -> None:
    try:
        config = load_config()
        identity = load_identity()
        models_config = load_models_config()

        if models_config.runtime.provider != "ollama":
            raise ModelConfigError(
                "O Atlas v0.1 suporta apenas o runtime 'ollama'."
            )

        runtime = OllamaRuntime(
            host=models_config.runtime.host,
            timeout_seconds=models_config.runtime.timeout_seconds,
        )

        atlas = Atlas(
            config=config,
            identity=identity,
            runtime=runtime,
            model_name=models_config.model.name,
        )

        status = atlas.start()

    except (
        AtlasConfigError,
        AtlasIdentityError,
        ModelConfigError,
        ValueError,
    ) as exc:
        print("=" * 72)
        print("Falha ao inicializar Atlas.")
        print("=" * 72)
        print(f"Erro: {exc}")
        print("=" * 72)

        sys.exit(1)

    print("=" * 72)
    print(f"{status.name} v{status.version}")
    print("=" * 72)

    print("Inicialização do núcleo concluída.")
    print(f"Status de inicialização: {status.startup_status}")
    print(f"Estado do sistema: {status.system_state.value}")
    print(f"Ambiente: {status.environment}")
    print(f"Idioma: {status.language}")

    print(
        "Offline-first: "
        f"{'ATIVO' if status.offline_first else 'INATIVO'}"
    )

    print(
        "Identidade: "
        f"{'CARREGADA' if status.identity_loaded else 'NÃO CARREGADA'}"
    )

    print(f"Tipo: {status.identity_type}")
    print(f"Princípios carregados: {status.principles_loaded}")

    print(
        "Componentes prontos: "
        f"{status.ready_components}/{status.total_components}"
    )

    print("-" * 72)

    for component in atlas.registry.all():
        print(
            f"{component.name:<20} "
            f"{component.state.value:<12} "
            f"{component.detail}"
        )

    print("=" * 72)


if __name__ == "__main__":
    main()
