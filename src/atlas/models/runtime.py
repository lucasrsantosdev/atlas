from __future__ import annotations

import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass


class ModelRuntimeError(RuntimeError):
    """Falha ao acessar um provedor de modelos."""


@dataclass(frozen=True)
class RuntimeHealth:
    available: bool
    provider: str
    detail: str


@dataclass(frozen=True)
class GenerationResult:
    model: str
    response: str
    provider: str = "unknown"
    input_tokens: int | None = None
    output_tokens: int | None = None


class ModelRuntime(ABC):
    @property
    @abstractmethod
    def provider(self) -> str: ...

    @abstractmethod
    def health(self) -> RuntimeHealth: ...

    @abstractmethod
    def generate(self, model: str, prompt: str, *, system_prompt: str | None = None) -> GenerationResult: ...


class OllamaRuntime(ModelRuntime):
    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def provider(self) -> str:
        return "ollama"

    def _request(self, path: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=data,
            headers={"Content-Type": "application/json"},
            method="POST" if payload is not None else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ModelRuntimeError(f"Ollama indisponível: {exc}") from exc

    def health(self) -> RuntimeHealth:
        try:
            self._request("/api/tags")
            return RuntimeHealth(True, self.provider, "Ollama disponível.")
        except ModelRuntimeError as exc:
            return RuntimeHealth(False, self.provider, str(exc))

    def generate(self, model: str, prompt: str, *, system_prompt: str | None = None) -> GenerationResult:
        payload = {"model": model, "prompt": prompt, "stream": False}
        if system_prompt:
            payload["system"] = system_prompt
        data = self._request("/api/generate", payload)
        response = str(data.get("response", "")).strip()
        if not response:
            raise ModelRuntimeError("Ollama retornou resposta vazia.")
        return GenerationResult(model=model, response=response, provider=self.provider,
                                input_tokens=data.get("prompt_eval_count"), output_tokens=data.get("eval_count"))
