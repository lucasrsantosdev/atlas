from __future__ import annotations

import argparse
import logging
import sys

from atlas.core import Atlas, AtlasConfigError, load_config
from atlas.identity import AtlasIdentityError, load_identity
from atlas.interfaces import print_status, run_chat
from atlas.logging import configure_logging
from atlas.models import (
    ModelConfigError,
    ModelRouter,
    ModelRouterError,
    load_models_config,
)
from atlas.models.runtime import OllamaRuntime


logger = logging.getLogger("atlas.main")


def build_atlas() -> Atlas:
    """
    Constrói a instância principal do Atlas v0.1.
    """

    logger.info("Iniciando construção do Atlas.")

    config = load_config()
    logger.info("Configuração carregada.")

    identity = load_identity()
    logger.info(
        "Identidade carregada: name=%s version=%s",
        identity.name,
        identity.version,
    )

    models_config = load_models_config()

    if models_config.runtime.provider != "ollama":
        raise ModelConfigError(
            "O Atlas v0.1 suporta apenas o runtime 'ollama'."
        )

    runtime = OllamaRuntime(
        host=models_config.runtime.host,
        timeout_seconds=models_config.runtime.timeout_seconds,
    )

    logger.info(
        "Runtime configurado: provider=%s host=%s",
        models_config.runtime.provider,
        models_config.runtime.host,
    )

    model_router = ModelRouter()

    model_router.register(
        role=models_config.model.role,
        model_name=models_config.model.name,
        runtime=runtime,
    )

    logger.info(
        "Modelo registrado: role=%s model=%s",
        models_config.model.role,
        models_config.model.name,
    )

    atlas = Atlas(
        config=config,
        identity=identity,
        model_router=model_router,
    )

    logger.info("Atlas construído com sucesso.")

    return atlas


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
    configure_logging()

    logger.info("Atlas CLI iniciado.")

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
        logger.exception(
            "Falha ao inicializar Atlas."
        )

        print("=" * 72)
        print("Falha ao inicializar Atlas.")
        print("=" * 72)
        print(f"Erro: {exc}")
        print("=" * 72)

        sys.exit(1)

    if args.command == "chat":
        logger.info("Modo chat iniciado.")
        run_chat(atlas)
        logger.info("Modo chat encerrado.")
        return

    logger.info("Exibindo status do sistema.")
    print_status(atlas)


if __name__ == "__main__":
    main()
