from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class ModelRuntimeError(RuntimeError):
    """Erro durante a execução de um runtime de modelo."""


@dataclass(frozen=True)
class RuntimeHealth:
    available: bool
    provider: str
    detail: str


@dataclass(frozen=True)
class GenerationResult:
    model: str
    response: str


class ModelRuntime(ABC):
    """
    Contrato comum para runtimes cognitivos do Atlas.

    O Atlas Core não depende diretamente de Ollama,
    llama.cpp ou qualquer outro runtime específico.
    """

    @property
    @abstractmethod
    def provider(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> RuntimeHealth:
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> GenerationResult:
        raise NotImplementedError
