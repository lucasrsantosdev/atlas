from collections.abc import Iterable

from app.context.manager import build_context
from app.models.conversation_repository import get_conversation
from app.models.message import Message
from app.models.message_repository import create_message, list_messages
from app.memory.manager import save_explicit_memory
from app.models.repository import get_model
from app.providers.ollama import OllamaProvider


def _get_provider(provider_name: str):
    if provider_name == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unsupported model provider: {provider_name}")


def chat(conversation_id: int, content: str) -> Message:
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")

    model = get_model(conversation.model_id)
    if model is None:
        raise ValueError("Model not found")

    previous_user = next(
        (message.content for message in reversed(list_messages(conversation_id)) if message.role == "user"),
        None,
    )
    create_message(conversation_id, "user", content)
    memory = save_explicit_memory(
        content,
        # Explicit user memory is global by default, even when saved from a project chat.
        # Project-scoped state is stored separately through project memory operations.
        project_id=None,
        previous_content=previous_user,
    )
    if memory is not None:
        return create_message(
            conversation_id,
            "assistant",
            f"Memória salva no Mosaic como {memory.type}: {memory.value}",
        )
    messages = build_context(conversation_id)

    provider = _get_provider(model.provider)
    response = provider.generate(
        messages=messages,
        model_name=model.model_name,
        configuration=model.configuration,
    )

    return create_message(conversation_id, "assistant", response)


def stream_chat(conversation_id: int, content: str) -> Iterable[str]:
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")

    model = get_model(conversation.model_id)
    if model is None:
        raise ValueError("Model not found")

    previous_user = next(
        (message.content for message in reversed(list_messages(conversation_id)) if message.role == "user"),
        None,
    )
    create_message(conversation_id, "user", content)
    memory = save_explicit_memory(
        content,
        # Explicit user memory is global by default, even when saved from a project chat.
        # Project-scoped state is stored separately through project memory operations.
        project_id=None,
        previous_content=previous_user,
    )
    if memory is not None:
        response = f"Memória salva no Mosaic como {memory.type}: {memory.value}"
        yield response
        create_message(conversation_id, "assistant", response)
        return
    messages = build_context(conversation_id)
    provider = _get_provider(model.provider)

    chunks: list[str] = []
    for chunk in provider.stream(
        messages=messages,
        model_name=model.model_name,
        configuration=model.configuration,
    ):
        chunks.append(chunk)
        yield chunk

    response = "".join(chunks).strip()
    if not response:
        raise RuntimeError("O modelo não retornou conteúdo na resposta.")
    create_message(conversation_id, "assistant", response)
