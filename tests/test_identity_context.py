from __future__ import annotations

import unittest

from atlas.identity import (
    build_identity_context,
    load_identity,
)


class TestIdentityContext(unittest.TestCase):

    def setUp(self) -> None:
        self.identity = load_identity()
        self.context = build_identity_context(
            self.identity
        )

    def test_context_identifies_atlas(self) -> None:
        self.assertIn(
            "You are Atlas.",
            self.context,
        )

    def test_context_contains_mission(self) -> None:
        self.assertIn(
            self.identity.mission,
            self.context,
        )

    def test_context_preserves_model_independence(self) -> None:
        self.assertIn(
            "replaceable cognitive",
            self.context,
        )

    def test_context_reports_memory_limitation(self) -> None:
        self.assertIn(
            "Persistent memory is not yet implemented.",
            self.context,
        )

    def test_context_uses_portuguese(self) -> None:
        self.assertIn(
            "Portuguese (Brazil)",
            self.context,
        )


if __name__ == "__main__":
    unittest.main()
