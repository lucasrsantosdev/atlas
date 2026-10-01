from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class EmbeddingError(RuntimeError):
    """Erro durante geração de embeddings."""


@dataclass(frozen=True)
class EmbeddingResult:
    """
    Resultado de embedding gerado pelo Atlas.
    """

    model: str
    vector: tuple[float, ...]

    @property
    def dimension(self) -> int:
        return len(self.vector)


class EmbeddingProvider(ABC):
    """
    Contrato substituível para geração de embeddings.
    """

    @abstractmethod
    def embed_text(
        self,
        text: str,
    ) -> EmbeddingResult:
        raise NotImplementedError

    @abstractmethod
    def embed_many(
        self,
        texts: tuple[str, ...],
    ) -> tuple[EmbeddingResult, ...]:
        raise NotImplementedError


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Provider de embeddings usando Ollama local.
    """

    def __init__(
        self,
        *,
        model: str = "nomic-embed-text",
        host: str = "http://127.0.0.1:11434",
        timeout_seconds: int = 30,
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        texts: tuple[str, ...],
    ) -> tuple[EmbeddingResult, ...]:
        if not texts:
            raise ValueError(
                "É necessário fornecer pelo menos um texto."
            )

        clean_texts = tuple(
            text.strip()
            for text in texts
        )

        if any(not text for text in clean_texts):
            raise ValueError(
                "Textos para embedding não podem estar vazios."
            )

        payload = {
            "model": self.model,
            "input": (
                clean_texts[0]
                if len(clean_texts) == 1
                else list(clean_texts)
            ),
        }

        request = Request(
            f"{self.host}/api/embed",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                raw_response = response.read()

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
        ) as exc:
            raise EmbeddingError(
                f"Falha ao acessar Ollama embeddings: {exc}"
            ) from exc

        try:
            data = json.loads(
                raw_response.decode("utf-8")
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise EmbeddingError(
                "Resposta inválida recebida do Ollama."
            ) from exc

        embeddings = data.get("embeddings")

        if not isinstance(embeddings, list):
            raise EmbeddingError(
                "Ollama não retornou embeddings válidos."
            )

        if len(embeddings) != len(clean_texts):
            raise EmbeddingError(
                "Quantidade de embeddings diferente "
                "da quantidade de textos enviados."
            )

        results: list[EmbeddingResult] = []

        for vector in embeddings:
            if not isinstance(vector, list):
                raise EmbeddingError(
                    "Vetor de embedding inválido."
                )

            results.append(
                EmbeddingResult(
                    model=self.model,
                    vector=tuple(
                        float(value)
                        for value in vector
                    ),
                )
            )

        return tuple(results)

    def embed_text(
        self,
        text: str,
    ) -> EmbeddingResult:
        return self._request(
            (text,)
        )[0]

    def embed_many(
        self,
        texts: tuple[str, ...],
    ) -> tuple[EmbeddingResult, ...]:
        return self._request(texts)
