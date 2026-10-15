from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any


class ModelProvider(ABC):
    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        model_name: str,
        configuration: dict[str, Any],
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def stream(
        self,
        messages: list[dict[str, str]],
        model_name: str,
        configuration: dict[str, Any],
    ) -> Iterable[str]:
        raise NotImplementedError
