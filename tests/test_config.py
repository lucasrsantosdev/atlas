from __future__ import annotations

import unittest

from atlas.core import load_config


class TestAtlasConfig(unittest.TestCase):

    def test_load_config(self) -> None:
        config = load_config()

        self.assertEqual(config.atlas.name, "Atlas")
        self.assertEqual(config.atlas.version, "0.1.0")

        self.assertTrue(config.runtime.offline_first)
        self.assertEqual(config.runtime.environment, "development")
        self.assertEqual(config.runtime.language, "pt-BR")

        self.assertEqual(
            config.system.startup_status,
            "BASE_READY",
        )


if __name__ == "__main__":
    unittest.main()
