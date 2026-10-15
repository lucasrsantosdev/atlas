import io
import json
from unittest.mock import patch

from app.providers.ollama import OllamaProvider


def _ollama_stream(*chunks):
    body = b"".join(
        (json.dumps(chunk, ensure_ascii=False) + "\n").encode("utf-8")
        for chunk in chunks
    )
    return io.BytesIO(body)


def _chunk(content="", *, done=False, thinking=None):
    message = {"role": "assistant", "content": content}
    if thinking is not None:
        message["thinking"] = thinking
    return {"message": message, "done": done}


def test_generate_extracts_qwen3_answer_after_thinking_marker():
    provider = OllamaProvider()
    provider._post = lambda path, payload: {
        "message": {
            "role": "assistant",
            "content": "Let me think through this carefully.\n</think>\nteste",
        }
    }

    result = provider.generate(
        messages=[{"role": "user", "content": "Responda teste"}],
        model_name="qwen3:4b",
        configuration={"think": False},
    )

    assert result == "teste"


def test_stream_suppresses_qwen3_inline_thinking_and_handles_split_marker():
    provider = OllamaProvider()
    response = _ollama_stream(
        _chunk("Reasoning that must not be shown."),
        _chunk("</thi"),
        _chunk("nk>\n"),
        _chunk("res"),
        _chunk("posta final"),
        _chunk(done=True),
    )

    with patch("app.providers.ollama.request.urlopen", return_value=response):
        result = list(
            provider.stream(
                messages=[{"role": "user", "content": "Responda"}],
                model_name="qwen3:4b",
                configuration={"think": False},
            )
        )

    assert "".join(result) == "resposta final"
    assert all("Reasoning" not in part and "</think>" not in part for part in result)


def test_stream_uses_content_when_ollama_separates_thinking_field():
    provider = OllamaProvider()
    response = _ollama_stream(
        _chunk("", thinking="Reasoning in a separate field"),
        _chunk("resposta "),
        _chunk("final"),
        _chunk(done=True),
    )

    with patch("app.providers.ollama.request.urlopen", return_value=response):
        result = list(
            provider.stream(
                messages=[{"role": "user", "content": "Responda"}],
                model_name="qwen3:4b",
                configuration={"think": True},
            )
        )

    assert result == ["resposta ", "final"]


def test_non_qwen3_models_keep_normal_streaming():
    provider = OllamaProvider()
    response = _ollama_stream(
        _chunk("Olá "),
        _chunk("mundo"),
        _chunk(done=True),
    )

    with patch("app.providers.ollama.request.urlopen", return_value=response):
        result = list(
            provider.stream(
                messages=[{"role": "user", "content": "Oi"}],
                model_name="llama3.2:3b",
                configuration={},
            )
        )

    assert result == ["Olá ", "mundo"]


def test_generate_keeps_normal_answer_without_marker():
    provider = OllamaProvider()
    provider._post = lambda path, payload: {
        "message": {"role": "assistant", "content": "  resposta normal  "}
    }

    result = provider.generate(
        messages=[{"role": "user", "content": "Oi"}],
        model_name="qwen3:4b",
        configuration={},
    )

    assert result == "resposta normal"



def test_generate_extracts_tagged_thinking_for_any_ollama_model():
    provider = OllamaProvider()
    provider._post = lambda path, payload: {
        "message": {
            "role": "assistant",
            "content": "<think>private reasoning</think>Resposta final.",
        }
    }

    result = provider.generate(
        messages=[{"role": "user", "content": "Responda"}],
        model_name="llama3.2:3b",
        configuration={},
    )

    assert result == "Resposta final."


def test_generate_does_not_expose_truncated_tagged_thinking():
    provider = OllamaProvider()
    provider._post = lambda path, payload: {
        "message": {
            "role": "assistant",
            "content": "<think>private reasoning without a closing marker",
        }
    }

    result = provider.generate(
        messages=[{"role": "user", "content": "Responda"}],
        model_name="llama3.2:3b",
        configuration={},
    )

    assert result == ""
