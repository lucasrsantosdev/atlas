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


def _print_knowledge_status(
    atlas: Atlas,
) -> None:
    status = atlas.knowledge_status()

    print("\nKnowledge:")
    print(
        f"  documentos: "
        f"{status.indexed_documents}"
    )
    print(
        f"  vectors: "
        f"{status.indexed_chunks}"
    )
    print(
        f"  lexical: "
        f"{status.lexical_chunks}"
    )
    print(
        f"  dimension: "
        f"{status.dimension}"
    )
    print(
        f"  fts5: "
        f"{status.fts_available}"
    )
    print(
        f"  index: "
        f"{status.index_path}"
    )


def _handle_knowledge_command(
    atlas: Atlas,
    user_input: str,
) -> bool:
    """
    Processa comandos /knowledge.

    Retorna True quando o comando foi tratado.
    """

    if not user_input.startswith(
        "/knowledge"
    ):
        return False

    parts = user_input.split(
        maxsplit=2
    )

    if len(parts) == 1:
        print(
            "\nUso:"
            "\n  /knowledge status"
            "\n  /knowledge index <caminho>"
            "\n  /knowledge save"
            "\n  /knowledge ask <pergunta>"
        )
        return True

    command = parts[1].lower()

    if command == "status":
        _print_knowledge_status(
            atlas
        )
        return True

    if command == "save":
        atlas.save_knowledge_index()

        print(
            "\nAtlas > "
            "Índice de conhecimento salvo."
        )

        return True

    if command == "index":
        if len(parts) < 3:
            print(
                "\nAtlas > "
                "Informe um caminho."
            )
            return True

        path = parts[2].strip()

        report = atlas.index_knowledge(
            path
        )

        print(
            "\nAtlas > "
            "Indexação concluída."
        )

        print(
            "Documentos:",
            report.documents,
        )

        print(
            "Chunks:",
            report.chunks,
        )

        return True

    if command == "ask":
        if len(parts) < 3:
            print(
                "\nAtlas > "
                "Informe uma pergunta."
            )
            return True

        question = parts[2].strip()

        result = atlas.ask_knowledge(
            question
        )

        print(
            f"\nAtlas > {result.response}"
        )

        return True

    print(
        "\nAtlas > "
        f"Comando Knowledge desconhecido: "
        f"{command}"
    )

    return True


def run_chat(atlas: Atlas) -> None:
    """
    Interface conversacional mínima do Atlas v0.1.
    """

    print("=" * 72)
    print(f"{atlas.name} — CLI local")
    print("=" * 72)
    print("Modelo local conectado através do Model Router.")
    print("Digite /exit para sair.")

    print(
        "Knowledge:"
        "\n  /knowledge status"
        "\n  /knowledge index <caminho>"
        "\n  /knowledge save"
        "\n  /knowledge ask <pergunta>"
    )

    print("=" * 72)

    while True:
        try:
            user_input = input(
                "\nVocê > "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt,
        ):
            print(
                "\nEncerrando Atlas."
            )
            return

        if not user_input:
            continue

        if user_input.lower() in {
            "/exit",
            "/quit",
            "exit",
            "quit",
        }:
            print(
                "Atlas > Até mais."
            )
            return

        try:
            if _handle_knowledge_command(
                atlas,
                user_input,
            ):
                continue

            result = atlas.process_message(
                user_input,
                role="primary",
            )

            print(
                f"\nAtlas > "
                f"{result.response}"
            )

        except (
            ModelRouterError,
            ModelRuntimeError,
            RuntimeError,
            ValueError,
        ) as exc:
            print(
                "\nAtlas > "
                f"Erro de execução: {exc}"
            )
