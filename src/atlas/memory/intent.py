from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class MemoryIntentAction(str, Enum):
    NONE = "none"
    WRITE = "write"
    RECALL = "recall"


@dataclass(frozen=True)
class MemoryIntent:
    action: MemoryIntentAction
    original_text: str
    content: str | None = None
    explicit_user_authorization: bool = False
    requires_clarification: bool = False
    matched_expression: str | None = None

    @property
    def is_memory_action(self) -> bool:
        return self.action != MemoryIntentAction.NONE

    @property
    def can_write(self) -> bool:
        return (
            self.action == MemoryIntentAction.WRITE
            and self.explicit_user_authorization
            and not self.requires_clarification
            and self.content is not None
            and bool(self.content.strip())
        )


class MemoryIntentDetector:
    """
    Detector determinístico de intenção de memória.

    Responsabilidades:
    - identificar autorização explícita;
    - respeitar negações;
    - extrair conteúdo quando presente;
    - sinalizar solicitações ambíguas;
    - identificar intenção de recuperação.

    Não grava nem recupera memória.
    """

    DENY_PATTERNS: tuple[str, ...] = (
        r"\bn[aã]o\s+memorize\b",
        r"\bn[aã]o\s+guarde\b",
        r"\bn[aã]o\s+salve\b",
        r"\bn[aã]o\s+se\s+lembre\b",
        r"\besque[cç]a\s+isso\b",
        r"\bpode\s+esquecer\b",
    )

    WRITE_WITH_CONTENT_PATTERNS: tuple[
        tuple[str, str],
        ...
    ] = (
        (
            r"\bmemorize(?:\s+esta\s+informa[cç][aã]o)?\s*[:,-]?\s+(?:que\s+)?(.+)",
            "memorize",
        ),
        (
            r"\blembre(?:-se)?\s+(?:de\s+)?(?:que\s+)?(.+)",
            "lembre",
        ),
        (
            r"\bguarde(?:\s+esta\s+informa[cç][aã]o)?\s*[:,-]?\s+(?:que\s+)?(.+)",
            "guarde",
        ),
        (
            r"\bsalve(?:\s+esta\s+informa[cç][aã]o)?\s*[:,-]?\s+(?:que\s+)?(.+)",
            "salve",
        ),
        (
            r"\bn[aã]o\s+esque[cç]a(?:\s+de)?\s+(?:que\s+)?(.+)",
            "não esqueça",
        ),
        (
            r"\bquero\s+que\s+voc[eê]\s+(?:se\s+)?lembre\s+(?:de\s+)?(?:que\s+)?(.+)",
            "quero que você lembre",
        ),
    )

    AMBIGUOUS_WRITE_PATTERNS: tuple[
        tuple[str, str],
        ...
    ] = (
        (
            r"\bmemorize\s+(?:isso|isto)\s*[.!?]*$",
            "memorize isso",
        ),
        (
            r"\bguarde\s+(?:isso|isto)\s*[.!?]*$",
            "guarde isso",
        ),
        (
            r"\blembre(?:-se)?\s+(?:disso|disto)\s*[.!?]*$",
            "lembre disso",
        ),
        (
            r"\bsalve\s+(?:isso|isto)\s*[.!?]*$",
            "salve isso",
        ),
        (
            r"\bn[aã]o\s+esque[cç]a\s+(?:disso|disto)\s*[.!?]*$",
            "não esqueça disso",
        ),
    )

    RECALL_PATTERNS: tuple[str, ...] = (
        r"\bo\s+que\s+voc[eê]\s+lembra\b",
        r"\bdo\s+que\s+voc[eê]\s+se\s+lembra\b",
        r"\bvoc[eê]\s+lembra\b",
        r"\brelembre\b",
        r"\brecupere\b",
        r"\bqual\s+(?:era|[ée])\b",
    )

    def detect(
        self,
        text: str,
    ) -> MemoryIntent:
        original_text = text.strip()

        if not original_text:
            return MemoryIntent(
                action=MemoryIntentAction.NONE,
                original_text="",
            )

        normalized = original_text.casefold()

        if self._matches_any(
            normalized,
            self.DENY_PATTERNS,
        ):
            return MemoryIntent(
                action=MemoryIntentAction.NONE,
                original_text=original_text,
                explicit_user_authorization=False,
                requires_clarification=False,
                matched_expression="memory_denial",
            )

        for (
            pattern,
            expression,
        ) in self.AMBIGUOUS_WRITE_PATTERNS:
            if re.search(
                pattern,
                original_text,
                flags=re.IGNORECASE,
            ):
                return MemoryIntent(
                    action=MemoryIntentAction.WRITE,
                    original_text=original_text,
                    content=None,
                    explicit_user_authorization=True,
                    requires_clarification=True,
                    matched_expression=expression,
                )

        for (
            pattern,
            expression,
        ) in self.WRITE_WITH_CONTENT_PATTERNS:
            match = re.search(
                pattern,
                original_text,
                flags=re.IGNORECASE,
            )

            if match is None:
                continue

            content = match.group(1).strip()

            if not content:
                return MemoryIntent(
                    action=MemoryIntentAction.WRITE,
                    original_text=original_text,
                    content=None,
                    explicit_user_authorization=True,
                    requires_clarification=True,
                    matched_expression=expression,
                )

            return MemoryIntent(
                action=MemoryIntentAction.WRITE,
                original_text=original_text,
                content=content,
                explicit_user_authorization=True,
                requires_clarification=False,
                matched_expression=expression,
            )

        if self._matches_any(
            normalized,
            self.RECALL_PATTERNS,
        ):
            return MemoryIntent(
                action=MemoryIntentAction.RECALL,
                original_text=original_text,
                content=original_text,
                explicit_user_authorization=False,
                requires_clarification=False,
                matched_expression="recall",
            )

        return MemoryIntent(
            action=MemoryIntentAction.NONE,
            original_text=original_text,
        )

    @staticmethod
    def _matches_any(
        text: str,
        patterns: tuple[str, ...],
    ) -> bool:
        return any(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            is not None
            for pattern in patterns
        )
