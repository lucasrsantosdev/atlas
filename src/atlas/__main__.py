from __future__ import annotations

import argparse
import sys

from atlas.core import Atlas, AtlasConfigError, load_config
from atlas.identity import AtlasIdentityError, load_identity
from atlas.interfaces import print_status, run_chat
from atlas.models import (
    ModelConfigError,
    ModelRouter,
    ModelRouterError,
    load_models_config,
)
from atlas.models.runtime import OllamaRuntime


def build_atlas() -> Atlas:
    """
    Constrói a instância principal do Atlas v0.1.
    """

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

    model_router = ModelRouter()

    model_router.register(
        role=models_config.model.role,
        model_name=models_config.model.name,
        runtime=runtime,
    )

    return Atlas(
        config=config,
        identity=identity,
        model_router=model_router,
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="ATLAS.IA — agente local offline-first.",
    )

    subcommands = parser.add_subparsers(
        dest="command",
    )

    subcommands.add_parser(
        "status",
        help="Exibe o estado do sistema Atlas.",
    )

    subcommands.add_parser(
        "chat",
        help="Inicia a interface conversacional local.",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    try:
        atlas = build_atlas()

    except (
        AtlasConfigError,
        AtlasIdentityError,
        ModelConfigError,
        ModelRouterError,
        ValueError,
    ) as exc:
        print("=" * 72)
        print("Falha ao inicializar Atlas.")
        print("=" * 72)
        print(f"Erro: {exc}")
        print("=" * 72)

        sys.exit(1)

    if args.command == "chat":
        run_chat(atlas)
        return

    print_status(atlas)


if __name__ == "__main__":
    main()
