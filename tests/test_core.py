from __future__ import annotations

import unittest

from atlas.core import Atlas, load_config
from atlas.identity import load_identity
from atlas.models import ModelRouter
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
        if system_prompt is None:
            raise AssertionError(
                "Atlas não enviou contexto de identidade."
            )

        if "You are Atlas." not in system_prompt:
            raise AssertionError(
                "Contexto não contém identidade Atlas."
            )

        return GenerationResult(
            model=model,
            response="ATLAS CORE TEST OK",
        )


class TestAtlasCore(unittest.TestCase):

    def setUp(self) -> None:
        config = load_config()
        identity = load_identity()

        runtime = FakeRuntime()

        router = ModelRouter()

        router.register(
            role="primary",
            model_name="fake-model",
            runtime=runtime,
        )

        self.atlas = Atlas(
            config=config,
            identity=identity,
            model_router=router,
        )

    def test_atlas_name(self) -> None:
        self.assertEqual(
            self.atlas.name,
            "Atlas",
        )

    def test_system_ready(self) -> None:
        status = self.atlas.start()

        self.assertEqual(
            status.system_state.value,
            "READY",
        )

    def test_identity_loaded(self) -> None:
        status = self.atlas.start()

        self.assertTrue(
            status.identity_loaded
        )

    def test_router_component_ready(self) -> None:
        component = self.atlas.registry.get(
            "model_router"
        )

        self.assertIsNotNone(component)

        self.assertEqual(
            component.state.value,
            "READY",
        )

    def test_generate_uses_identity_context(self) -> None:
        result = self.atlas.generate(
            "teste"
        )

        self.assertEqual(
            result.response,
            "ATLAS CORE TEST OK",
        )


if __name__ == "__main__":
    unittest.main()
