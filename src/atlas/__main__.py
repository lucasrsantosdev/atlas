from __future__ import annotations

import sys

from atlas.core import Atlas, AtlasConfigError, load_config
from atlas.identity import AtlasIdentityError, load_identity


def main() -> None:
    try:
        config = load_config()
        identity = load_identity()

        atlas = Atlas(
            config=config,
            identity=identity,
        )

        status = atlas.start()

    except (AtlasConfigError, AtlasIdentityError, ValueError) as exc:
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
    print(f"Status: {status.status}")
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
    print("=" * 72)


if __name__ == "__main__":
    main()