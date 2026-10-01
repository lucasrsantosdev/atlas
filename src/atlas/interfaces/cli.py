from __future__ import annotations

from atlas.core import Atlas
from atlas.models import ModelRouterError
from atlas.models.runtime import ModelRuntimeError


def print_status(atlas: Atlas) -> None:
    """
    Exibe o estado atual do Atlas.
    """

    status = atlas.start()

    print("=" * 72)
    print(f"{status.name} v{status.version}")
    print("=" * 72)
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


def run_chat(atlas: Atlas) -> None:
    """
    Interface conversacional mínima do Atlas v0.1.
    """

    print("=" * 72)
    print(f"{atlas.name} — CLI local")
    print("=" * 72)
    print("Modelo local conectado através do Model Router.")
    print("Digite /exit para sair.")
    print("=" * 72)

    while True:
        try:
            user_input = input("\nVocê > ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando Atlas.")
            return

        if not user_input:
            continue

        if user_input.lower() in {
            "/exit",
            "/quit",
            "exit",
            "quit",
        }:
            print("Atlas > Até mais.")
            return

        try:
            result = atlas.process_message(
                user_input,
                role="primary",
            )

            print(f"\nAtlas > {result.response}")

        except (ModelRouterError, ModelRuntimeError) as exc:
            print(f"\nAtlas > Erro de execução: {exc}")
