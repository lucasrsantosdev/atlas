from __future__ import annotations

import unittest

from atlas.models import (
    ModelRouter,
    ModelRouterError,
)
from atlas.models.runtime import (
    GenerationResult,
    ModelRuntime,
    RuntimeHealth,
)


class FakeRuntime(ModelRuntime):

    @property
    def provider(self) -> str:
        return "fake"

    def health(self) -> RuntimeHealth:
        return RuntimeHealth(
            available=True,
            provider=self.provider,
            detail="Fake runtime ready.",
        )

    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> GenerationResult:
        return GenerationResult(
            model=model,
            response="FAKE RESPONSE",
        )


class TestModelRouter(unittest.TestCase):

    def setUp(self) -> None:
        self.runtime = FakeRuntime()
        self.router = ModelRouter()

        self.router.register(
            role="primary",
            model_name="fake-model",
            runtime=self.runtime,
        )

    def test_primary_route_exists(self) -> None:
        route = self.router.get_route("primary")

        self.assertEqual(
            route.model_name,
            "fake-model",
        )

    def test_router_status_ready(self) -> None:
        status = self.router.status()

        self.assertTrue(status.ready)
        self.assertEqual(
            status.registered_routes,
            1,
        )

    def test_generate_through_router(self) -> None:
        result = self.router.generate(
            "teste",
            role="primary",
        )

        self.assertEqual(
            result.response,
            "FAKE RESPONSE",
        )

    def test_unknown_route_is_rejected(self) -> None:
        with self.assertRaises(ModelRouterError):
            self.router.get_route("science")


if __name__ == "__main__":
    unittest.main()
