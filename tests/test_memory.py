from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atlas.memory import (
    JsonlMemoryStore,
    MemoryAuthorizationError,
    MemoryIntentAction,
    MemoryIntentDetector,
    MemoryRecord,
    MemoryService,
    MemorySource,
    MemoryType,
    MemoryVerification,
    build_memory_context,
)


class TestMemoryRecord(unittest.TestCase):

    def test_create_memory_record(self) -> None:
        memory = MemoryRecord.create(
            memory_type=MemoryType.PROJECTS,
            content="Atlas memory test.",
            source=MemorySource.USER,
            verification=MemoryVerification.USER_CONFIRMED,
            authorized=True,
            tags=("atlas", "test"),
        )

        self.assertTrue(memory.id)
        self.assertEqual(
            memory.memory_type,
            MemoryType.PROJECTS,
        )
        self.assertEqual(
            memory.content,
            "Atlas memory test.",
        )
        self.assertTrue(memory.authorized)

    def test_empty_content_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryRecord.create(
                memory_type=MemoryType.PROJECTS,
                content="   ",
                source=MemorySource.USER,
            )

    def test_invalid_confidence_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MemoryRecord.create(
                memory_type=MemoryType.PROJECTS,
                content="test",
                source=MemorySource.USER,
                confidence=2.0,
            )


class TestMemoryPersistence(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

        self.root = Path(
            self.temp_dir.name
        )

        self.store = JsonlMemoryStore(
            root_path=self.root
        )

        self.service = MemoryService(
            store=self.store
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_authorized_memory_is_persisted(self) -> None:
        memory = self.service.remember(
            memory_type=MemoryType.PROJECTS,
            content="ORION-27",
            source=MemorySource.USER,
            explicit_user_authorization=True,
            verification=MemoryVerification.USER_CONFIRMED,
            tags=("atlas", "orion"),
        )

        recovered = self.store.get_by_id(
            memory.id
        )

        self.assertIsNotNone(recovered)
        self.assertEqual(
            recovered.content,
            "ORION-27",
        )

    def test_memory_survives_new_service_instance(self) -> None:
        self.service.remember(
            memory_type=MemoryType.PROJECTS,
            content="Persistent restart test.",
            source=MemorySource.USER,
            explicit_user_authorization=True,
        )

        second_store = JsonlMemoryStore(
            root_path=self.root
        )

        second_service = MemoryService(
            store=second_store
        )

        memories = second_service.recall_text(
            "restart"
        )

        self.assertEqual(
            len(memories),
            1,
        )

        self.assertEqual(
            memories[0].content,
            "Persistent restart test.",
        )

    def test_unapproved_memory_is_blocked(self) -> None:
        with self.assertRaises(
            MemoryAuthorizationError
        ):
            self.service.remember(
                memory_type=MemoryType.OBSERVATIONS,
                content="Atlas inferred this.",
                source=MemorySource.ATLAS,
            )

    def test_system_history_is_allowed(self) -> None:
        memory = self.service.remember(
            memory_type=MemoryType.TIMELINE,
            content="Atlas system event.",
            source=MemorySource.SYSTEM,
            system_owned=True,
            verification=(
                MemoryVerification.SYSTEM_VERIFIED
            ),
        )

        self.assertTrue(memory.authorized)

        self.assertEqual(
            memory.metadata["authorization"]["reason"],
            "system_history",
        )

    def test_system_cannot_write_people_by_default(
        self,
    ) -> None:
        with self.assertRaises(
            MemoryAuthorizationError
        ):
            self.service.remember(
                memory_type=MemoryType.PEOPLE,
                content="Person information.",
                source=MemorySource.SYSTEM,
                system_owned=True,
            )

    def test_recall_by_text(self) -> None:
        self.service.remember(
            memory_type=MemoryType.DECISIONS,
            content=(
                "Atlas memory backend uses JSONL."
            ),
            source=MemorySource.USER,
            explicit_user_authorization=True,
        )

        memories = self.service.recall_text(
            "JSONL"
        )

        self.assertEqual(
            len(memories),
            1,
        )

    def test_recall_by_tags(self) -> None:
        self.service.remember(
            memory_type=MemoryType.PROJECTS,
            content="Atlas milestone.",
            source=MemorySource.USER,
            explicit_user_authorization=True,
            tags=("atlas", "milestone"),
        )

        memories = self.service.recall_tags(
            ("atlas", "milestone")
        )

        self.assertEqual(
            len(memories),
            1,
        )

    def test_recent_memories(self) -> None:
        self.service.remember(
            memory_type=MemoryType.PROJECTS,
            content="Memory one.",
            source=MemorySource.USER,
            explicit_user_authorization=True,
        )

        self.service.remember(
            memory_type=MemoryType.PROJECTS,
            content="Memory two.",
            source=MemorySource.USER,
            explicit_user_authorization=True,
        )

        memories = self.service.recall_recent(
            limit=1
        )

        self.assertEqual(
            len(memories),
            1,
        )

        self.assertEqual(
            memories[0].content,
            "Memory two.",
        )


class TestMemoryContext(unittest.TestCase):

    def test_memory_context(self) -> None:
        memory = MemoryRecord.create(
            memory_type=MemoryType.PROJECTS,
            content="ORION-27",
            source=MemorySource.USER,
            verification=MemoryVerification.USER_CONFIRMED,
            authorized=True,
            tags=("atlas",),
        )

        context = build_memory_context(
            (memory,)
        )

        self.assertIn(
            "ORION-27",
            context,
        )

        self.assertIn(
            "user_confirmed",
            context,
        )

    def test_empty_memory_context(self) -> None:
        self.assertEqual(
            build_memory_context(()),
            "",
        )


class TestMemoryIntent(unittest.TestCase):

    def setUp(self) -> None:
        self.detector = MemoryIntentDetector()

    def test_explicit_memory_write(self) -> None:
        intent = self.detector.detect(
            "Memorize que o código é ORION-27."
        )

        self.assertEqual(
            intent.action,
            MemoryIntentAction.WRITE,
        )

        self.assertTrue(
            intent.explicit_user_authorization
        )

        self.assertTrue(
            intent.can_write
        )

    def test_normal_conversation_is_not_memory(self) -> None:
        intent = self.detector.detect(
            "Meu projeto usa PostgreSQL."
        )

        self.assertEqual(
            intent.action,
            MemoryIntentAction.NONE,
        )

        self.assertFalse(
            intent.can_write
        )

    def test_memory_denial(self) -> None:
        intent = self.detector.detect(
            "Não guarde isso."
        )

        self.assertEqual(
            intent.action,
            MemoryIntentAction.NONE,
        )

        self.assertFalse(
            intent.explicit_user_authorization
        )

    def test_ambiguous_memory_requires_clarification(
        self,
    ) -> None:
        intent = self.detector.detect(
            "Guarde isso."
        )

        self.assertEqual(
            intent.action,
            MemoryIntentAction.WRITE,
        )

        self.assertTrue(
            intent.requires_clarification
        )

        self.assertFalse(
            intent.can_write
        )

    def test_recall_intent(self) -> None:
        intent = self.detector.detect(
            "Você lembra qual era o codinome?"
        )

        self.assertEqual(
            intent.action,
            MemoryIntentAction.RECALL,
        )


if __name__ == "__main__":
    unittest.main()
