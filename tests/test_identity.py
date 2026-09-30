from __future__ import annotations

import unittest

from atlas.identity import load_identity


class TestAtlasIdentity(unittest.TestCase):

    def test_load_identity(self) -> None:
        identity = load_identity()

        self.assertEqual(identity.name, "Atlas")
        self.assertEqual(identity.version, "0.1.0")
        self.assertEqual(
            identity.agent_type,
            "persistent_artificial_agent",
        )

    def test_identity_has_principles(self) -> None:
        identity = load_identity()

        self.assertGreater(
            len(identity.principles),
            0,
        )

    def test_identity_is_offline_first(self) -> None:
        identity = load_identity()

        self.assertTrue(
            identity.architecture["offline_first"]
        )

    def test_identity_is_model_independent(self) -> None:
        identity = load_identity()

        self.assertTrue(
            identity.architecture["model_independent"]
        )


if __name__ == "__main__":
    unittest.main()
