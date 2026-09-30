from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from atlas.models.runtime import (
    GenerationResult,
    ModelRuntime,
    ModelRuntimeError,
)


logger = logging.getLogger("atlas.models.router")


class ModelRouterError(RuntimeError):
    """Erro de roteamento de modelos do Atlas."""


@dataclass(frozen=True)
class ModelRoute:
    role: str
    model_name: str
    runtime: ModelRuntime


@dataclass(frozen=True)
class RouterStatus:
    ready: bool
    registered_routes: int
    available_roles: tuple[str, ...]
    detail: str


class ModelRouter:
    """
    Model Router mínimo do Atlas.
    """

    def __init__(self) -> None:
        self._routes: dict[str, ModelRoute] = {}

    def register(
        self,
        *,
        role: str,
        model_name: str,
        runtime: ModelRuntime,
    ) -> None:
        normalized_role = role.strip().lower()
        normalized_model = model_name.strip()

        if not normalized_role:
            raise ModelRouterError(
                "A função do modelo não pode estar vazia."
            )

        if not normalized_model:
            raise ModelRouterError(
                "O nome do modelo não pode estar vazio."
            )

        self._routes[normalized_role] = ModelRoute(
            role=normalized_role,
            model_name=normalized_model,
            runtime=runtime,
        )

        logger.info(
            "Rota registrada: role=%s model=%s provider=%s",
            normalized_role,
            normalized_model,
            runtime.provider,
        )

    def get_route(self, role: str) -> ModelRoute:
        normalized_role = role.strip().lower()

        route = self._routes.get(normalized_role)

        if route is None:
            logger.warning(
                "Rota inexistente solicitada: role=%s",
                normalized_role,
            )

            raise ModelRouterError(
                f"Nenhum modelo registrado para a função '{normalized_role}'."
            )

        return route

    def available_roles(self) -> tuple[str, ...]:
        return tuple(self._routes.keys())

    def status(self) -> RouterStatus:
        if not self._routes:
            return RouterStatus(
                ready=False,
                registered_routes=0,
                available_roles=(),
                detail="Nenhuma rota de modelo registrada.",
            )

        unavailable_roles: list[str] = []

        for role, route in self._routes.items():
            health = route.runtime.health()

            if not health.available:
                unavailable_roles.append(role)

        if unavailable_roles:
            return RouterStatus(
                ready=False,
                registered_routes=len(self._routes),
                available_roles=self.available_roles(),
                detail=(
                    "Runtimes indisponíveis para: "
                    + ", ".join(unavailable_roles)
                ),
            )

        return RouterStatus(
            ready=True,
            registered_routes=len(self._routes),
            available_roles=self.available_roles(),
            detail=(
                f"Model Router ativo com "
                f"{len(self._routes)} rota(s)."
            ),
        )

    def generate(
        self,
        prompt: str,
        *,
        role: str = "primary",
    ) -> GenerationResult:
        route = self.get_route(role)

        health = route.runtime.health()

        if not health.available:
            logger.error(
                "Runtime indisponível: role=%s model=%s",
                route.role,
                route.model_name,
            )

            raise ModelRuntimeError(
                f"Runtime da função '{route.role}' está indisponível."
            )

        logger.info(
            "Iniciando geração: role=%s model=%s",
            route.role,
            route.model_name,
        )

        started_at = time.perf_counter()

        result = route.runtime.generate(
            model=route.model_name,
            prompt=prompt,
        )

        elapsed_seconds = time.perf_counter() - started_at

        logger.info(
            "Geração concluída: role=%s model=%s duration=%.2fs",
            route.role,
            route.model_name,
            elapsed_seconds,
        )

        return result
