import json


from app.providers.ollama import OllamaProvider


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body

    def __iter__(self):
        return iter(self.body.splitlines())


def test_ollama_generate_sends_model_messages_and_configuration(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request):
        captured["request"] = request
        return FakeResponse(json.dumps({"message": {"content": "Olá"}}).encode())

    monkeypatch.setattr("app.providers.ollama.request.urlopen", fake_urlopen)

    provider = OllamaProvider("http://ollama.test")
    result = provider.generate(
        [{"role": "user", "content": "Olá"}],
        "qwen3:3b",
        {"temperature": 0.2, "unsupported": "ignored"},
    )

    payload = json.loads(captured["request"].data.decode())
    assert result == "Olá"
    assert captured["request"].full_url == "http://ollama.test/api/chat"
    assert payload["model"] == "qwen3:3b"
    assert payload["messages"] == [{"role": "user", "content": "Olá"}]
    assert payload["stream"] is False
    assert payload["think"] is False
    assert payload["options"] == {"temperature": 0.2}


def test_ollama_stream_yields_content_chunks(monkeypatch) -> None:
    body = b'{"message":{"content":"Ol"}}
{"message":{"content":"á"}}
{"done":true}
'
    monkeypatch.setattr(
        "app.providers.ollama.request.urlopen",
        lambda request: FakeResponse(body),
    )

    provider = OllamaProvider("http://ollama.test")
    assert list(provider.stream([{"role": "user", "content": "Olá"}], "qwen3:3b", {})) == ["Ol", "á"]


def test_ollama_stream_handles_empty_content_chunks(monkeypatch) -> None:
    body = b'{"message":{}}
{"message":{"content":"ok"}}
{"done":true}
'
    monkeypatch.setattr(
        "app.providers.ollama.request.urlopen",
        lambda request: FakeResponse(body),
    )

    provider = OllamaProvider("http://ollama.test")
    assert list(provider.stream([{"role": "user", "content": "Olá"}], "qwen3:3b", {})) == ["ok"]



def test_ollama_thinking_flag_can_be_configured(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request):
        captured["payload"] = json.loads(request.data.decode())
        return FakeResponse(b'{"message":{"content":"Resposta direta"},"done":true}\n')

    monkeypatch.setattr("app.providers.ollama.request.urlopen", fake_urlopen)

    provider = OllamaProvider("http://ollama.test")
    list(provider.stream(
        [{"role": "user", "content": "Oi"}],
        "qwen3:4b",
        {"think": True},
    ))

    assert captured["payload"]["think"] is True
