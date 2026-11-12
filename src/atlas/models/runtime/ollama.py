from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from atlas.models.runtime.base import (
    GenerationResult,
    ModelRuntime,
    ModelRuntimeError,
    RuntimeHealth,
)


class OllamaRuntime(ModelRuntime):
    """
    Adapter local para Ollama.

    Responsabilidades atuais:
    - verificar disponibilidade;
    - executar geração de texto;
    - receber contexto de sistema fornecido pelo Atlas.
    """

    def __init__(
        self,
        host: str = "http://127.0.0.1:11434",
        timeout_seconds: int = 120,
    ) -> None:
        self.host = host.rstrip("/")
        self.timeout_seconds = timeout_seconds

    @property
    def provider(self) -> str:
        return "ollama"

    def health(self) -> RuntimeHealth:
        url = f"{self.host}/api/tags"

        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                payload = response.read()

            data = json.loads(payload.decode("utf-8"))

            if not isinstance(data, dict):
                return RuntimeHealth(
                    available=False,
                    provider=self.provider,
                    detail="Resposta inesperada do runtime.",
                )

            models = data.get("models", [])

            return RuntimeHealth(
                available=True,
                provider=self.provider,
                detail=(
                    "Runtime Ollama disponível. "
                    f"Modelos detectados: {len(models)}."
                ),
            )

        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return RuntimeHealth(
                available=False,
                provider=self.provider,
                detail=f"Runtime Ollama indisponível: {exc}",
            )

        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return RuntimeHealth(
                available=False,
                provider=self.provider,
                detail=f"Resposta inválida do runtime: {exc}",
            )

    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> GenerationResult:
        if not model.strip():
            raise ModelRuntimeError(
                "Nome do modelo não pode estar vazio."
            )

        if not prompt.strip():
            raise ModelRuntimeError(
                "Prompt não pode estar vazio."
            )

        url = f"{self.host}/api/generate"

        request_body: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        if system_prompt:
            request_body["system"] = system_prompt

        body = json.dumps(
            request_body
        ).encode("utf-8")

        request = Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                payload = response.read()

            data = json.loads(payload.decode("utf-8"))

        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ModelRuntimeError(
                f"Falha ao executar o modelo '{model}': {exc}"
            ) from exc

        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelRuntimeError(
                f"Resposta inválida do runtime: {exc}"
            ) from exc

        generated_text = data.get("response")

        if not isinstance(generated_text, str):
            raise ModelRuntimeError(
                "O runtime não retornou uma resposta textual válida."
            )

        return GenerationResult(
            model=model,
            response=generated_text.strip(),
        )
