import pytest
from fastapi.testclient import TestClient

from app.db.database import init_db
from app.main import app
from app.memory.manager import remember
from app.models.message_repository import create_message, list_messages
from app.models.project_repository import create_project
from app.models.repository import create_model


@pytest.fixture(autouse=True)
def test_database(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.database.DATABASE_PATH", tmp_path / "test.db")
    init_db()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _conversation(client: TestClient) -> int:
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    response = client.post(
        "/conversations",
        json={"title": "Chat test", "model_id": model.id},
    )
    return response.json()["id"]


def test_chat_flow_persists_user_and_assistant_messages(client, monkeypatch) -> None:
    conversation_id = _conversation(client)

    def fake_generate(self, messages, model_name, configuration):
        assert messages[-1] == {"role": "user", "content": "Olá"}
        assert messages[0]["role"] == "system"
        assert "identidade" in messages[0]["content"]
        assert model_name == "qwen3:3b"
        return "Olá! Como posso ajudar?"

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", fake_generate)

    response = client.post(
        f"/conversations/{conversation_id}/chat",
        json={"content": "Olá"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "assistant"
    assert response.json()["content"] == "Olá! Como posso ajudar?"

    messages = list_messages(conversation_id)
    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == [
        "Olá",
        "Olá! Como posso ajudar?",
    ]


def test_chat_flow_uses_previous_history(client, monkeypatch) -> None:
    conversation_id = _conversation(client)
    calls = []

    def fake_generate(self, messages, model_name, configuration):
        calls.append(messages)
        return "Resposta"

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", fake_generate)

    client.post(f"/conversations/{conversation_id}/chat", json={"content": "Primeira"})
    client.post(f"/conversations/{conversation_id}/chat", json={"content": "Segunda"})

    assert calls[1][0]["role"] == "system"
    assert "identidade" in calls[1][0]["content"]
    assert calls[1][-3:] == [
        {"role": "user", "content": "Primeira"},
        {"role": "assistant", "content": "Resposta"},
        {"role": "user", "content": "Segunda"},
    ]


def test_chat_stream_returns_sse_and_persists_response(client, monkeypatch) -> None:
    conversation_id = _conversation(client)

    def fake_stream(self, messages, model_name, configuration):
        yield "Olá "
        yield "em "
        yield "stream"

    monkeypatch.setattr("app.services.chat.OllamaProvider.stream", fake_stream)

    response = client.post(
        f"/conversations/{conversation_id}/chat/stream",
        json={"content": "Oi"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert 'data: "Olá "' in response.text
    assert 'data: "em "' in response.text
    assert 'data: "stream"' in response.text
    assert "data: [DONE]" in response.text

    messages = list_messages(conversation_id)
    assert [message.content for message in messages] == ["Oi", "Olá em stream"]


def test_chat_returns_404_for_unknown_conversation(client) -> None:
    response = client.post(
        "/conversations/999999/chat",
        json={"content": "Olá"},
    )

    assert response.status_code == 404


def test_chat_passes_project_state_and_memory_to_provider(client, monkeypatch) -> None:
    project = create_project(
        name="Guitar Livre",
        workspace="/tmp/guitar-livre",
        state={"phase": "development"},
    )
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = client.post(
        "/conversations",
        json={
            "title": "Context integration",
            "model_id": model.id,
            "project_id": project.id,
        },
    ).json()

    remember(
        type="project_state",
        key="focus",
        value="Integrar o contexto do projeto",
        source="conversation",
        project_id=project.id,
    )

    captured = {}

    def fake_generate(self, messages, model_name, configuration):
        captured["messages"] = messages
        return "Contexto recebido"

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", fake_generate)

    response = client.post(
        f"/conversations/{conversation['id']}/chat",
        json={"content": "Onde estamos?"},
    )

    assert response.status_code == 200
    assert "identidade" in captured["messages"][0]["content"]
    assert any(
        item["role"] == "system" and "Mosaic project state:" in item["content"]
        and "{'phase': 'development'}" in item["content"]
        for item in captured["messages"]
    )
    assert any(
        item["role"] == "system" and "Mosaic memory" in item["content"]
        and "[project_state] focus: Integrar o contexto do projeto" in item["content"]
        for item in captured["messages"]
    )
    assert captured["messages"][-1] == {
        "role": "user",
        "content": "Onde estamos?",
    }



def test_explicit_memory_request_is_saved_without_calling_model(client, monkeypatch) -> None:
    project = create_project(name="Memory scope", workspace="/tmp/memory-scope")
    model = create_model("Qwen 3B", "ollama", "qwen3:3b")
    conversation = client.post(
        "/conversations",
        json={"title": "Project chat", "model_id": model.id, "project_id": project.id},
    ).json()
    conversation_id = conversation["id"]

    def unexpected_generate(*args, **kwargs):
        raise AssertionError("explicit memory commands should be handled by Mosaic Core")

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", unexpected_generate)

    response = client.post(
        f"/conversations/{conversation_id}/chat",
        json={"content": "Mosaic, salve que o Brasil foi descoberto em 2002"},
    )

    assert response.status_code == 200
    assert "Memória salva no Mosaic como user_claim" in response.json()["content"]

    memories_response = client.get("/memories")
    assert memories_response.status_code == 200
    saved = [item for item in memories_response.json() if item["value"] == "o Brasil foi descoberto em 2002"]
    assert len(saved) == 1
    assert saved[0]["type"] == "user_claim"
    assert saved[0]["source"] == "user"
    assert saved[0]["project_id"] is None

    next_conversation = client.post(
        "/conversations",
        json={"title": "Memory recall", "model_id": model.id},
    ).json()
    captured = {}

    def capture_context(self, messages, model_name, configuration):
        captured["messages"] = messages
        return "Lembro do registro salvo."

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", capture_context)
    recall_response = client.post(
        f"/conversations/{next_conversation['id']}/chat",
        json={"content": "O que você lembra sobre o Brasil?"},
    )

    assert recall_response.status_code == 200
    assert any(
        item["role"] == "system"
        and "Mosaic memory" in item["content"]
        and "o Brasil foi descoberto em 2002" in item["content"]
        for item in captured["messages"]
    )


def test_explicit_preference_memory_is_classified(client) -> None:
    conversation_id = _conversation(client)

    response = client.post(
        f"/conversations/{conversation_id}/chat",
        json={"content": "Mosaic, salve que eu gosto de música house"},
    )

    assert response.status_code == 200
    assert "user_preference" in response.json()["content"]

    memories = client.get("/memories").json()
    assert any(
        item["type"] == "user_preference" and item["value"] == "eu gosto de música house"
        for item in memories
    )



def test_save_this_information_uses_previous_user_statement(client) -> None:
    conversation_id = _conversation(client)

    create_message(conversation_id, "user", "O Brasil foi descoberto em 2002")

    saved = client.post(
        f"/conversations/{conversation_id}/chat",
        json={"content": "Mosaic, salve essa informação"},
    )
    assert saved.status_code == 200
    assert "user_claim" in saved.json()["content"]

    memories = client.get("/memories").json()
    assert any(
        item["type"] == "user_claim"
        and item["value"] == "O Brasil foi descoberto em 2002"
        for item in memories
    )


def test_memory_api_can_clear_project_scope(client) -> None:
    project = create_project(name="Memory scope API", workspace="/tmp/memory-scope-api")
    response = client.post(
        "/memories",
        json={
            "type": "user_claim",
            "key": "alegacao",
            "value": "o Brasil foi descoberto em 2002",
            "source": "user",
            "project_id": project.id,
        },
    )
    assert response.status_code == 200
    memory_id = response.json()["id"]

    updated = client.patch(f"/memories/{memory_id}", json={"project_id": None})

    assert updated.status_code == 200
    assert updated.json()["project_id"] is None


def test_save_to_memory_phrase_is_clean_and_retrievable_in_new_conversation(client, monkeypatch) -> None:
    conversation_id = _conversation(client)

    response = client.post(
        f"/conversations/{conversation_id}/chat",
        json={"content": "Salve na memória que a Alemanha foi descoberto em 2002"},
    )

    assert response.status_code == 200
    assert response.json()["content"] == (
        "Memória salva no Mosaic como user_claim: a Alemanha foi descoberto em 2002"
    )

    memories = client.get("/memories").json()
    saved = [item for item in memories if "Alemanha" in item["value"]]
    assert len(saved) == 1
    assert saved[0]["value"] == "a Alemanha foi descoberto em 2002"
    assert saved[0]["project_id"] is None

    next_conversation_id = _conversation(client)
    captured = {}

    def capture_context(self, messages, model_name, configuration):
        captured["messages"] = messages
        return "O registro foi encontrado no contexto."

    monkeypatch.setattr("app.services.chat.OllamaProvider.generate", capture_context)
    recall = client.post(
        f"/conversations/{next_conversation_id}/chat",
        json={"content": "O que você lembra sobre o que conversamos a respeito da Alemanha?"},
    )

    assert recall.status_code == 200
    assert any(
        item["role"] == "system"
        and "Mosaic memory" in item["content"]
        and "[user_claim] alegacao: a Alemanha foi descoberto em 2002" in item["content"]
        for item in captured["messages"]
    )
