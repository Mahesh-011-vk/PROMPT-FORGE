"""
PromptForge AI - PII (Personally Identifiable Information) Scrubber.

Detects and redacts sensitive data such as emails, phone numbers, SSNs, credit cards, and API keys.
"""

from __future__ import annotations

import re
from typing import ClassVar


class PIIScrubber:
    """Detects and redacts sensitive personally identifiable information."""

    PATTERNS: ClassVar[dict[str, tuple[re.Pattern, str]]] = {
        "EMAIL": (
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "[REDACTED_EMAIL]",
        ),
        "CREDIT_CARD": (
            re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
            "[REDACTED_CREDIT_CARD]",
        ),
        "SSN": (
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "[REDACTED_SSN]",
        ),
        "API_KEY": (
            re.compile(r"\b(?:sk-[A-Za-z0-9-_]{20,}|Bearer\s+[A-Za-z0-9-_]{25,})\b"),
            "[REDACTED_API_KEY]",
        ),
        "PHONE": (
            re.compile(r"\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            "[REDACTED_PHONE]",
        ),
    }

    @classmethod
    def scrub(cls, text: str) -> tuple[str, list[str]]:
        """Scan text and redact detected PII entities.

        Returns:
            Tuple of (scrubbed_text, list_of_detected_pii_types)
        """
        scrubbed = text
        detected: list[str] = []

        for pii_type, (pattern, replacement) in cls.PATTERNS.items():
            if pattern.search(scrubbed):
                detected.append(pii_type)
                scrubbed = pattern.sub(replacement, scrubbed)

        return scrubbed, detected
