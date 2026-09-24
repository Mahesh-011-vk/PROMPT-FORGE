"""
PromptForge AI - Prompt Injection & Adversarial Payload Guard.

Detects direct instruction overrides, jailbreak exploits, delimiter hijacking,
and system prompt extraction vectors.
"""

from __future__ import annotations

import re


class InjectionGuard:
    """Multi-vector detector for adversarial prompt injection payloads."""

    INJECTION_RULES: list[tuple[re.Pattern, str, float]] = [
        # (Pattern, Description, Weight)
        (
            re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
            "Direct override: instruction reset attempt",
            0.85,
        ),
        (
            re.compile(r"disregard\s+(all\s+)?(previous|prior|preceding)\s+(rules|prompts|directives)", re.I),
            "Direct override: rule disregard attempt",
            0.85,
        ),
        (
            re.compile(r"you\s+are\s+now\s+(in\s+)?(DAN|unrestricted|god)\s+mode", re.I),
            "Jailbreak: persona hijack (DAN/unrestricted)",
            0.90,
        ),
        (
            re.compile(r"(enable|activate)\s+(developer|unaligned|maintenance)\s+mode", re.I),
            "Jailbreak: developer mode simulation",
            0.75,
        ),
        (
            re.compile(r"(reveal|print|display|dump|leak)\s+(your\s+)?(system\s+prompt|initial\s+instructions)", re.I),
            "Prompt leakage: system prompt extraction attempt",
            0.80,
        ),
        (
            re.compile(r"(</system>|<system>|</instruction>|\[SYSTEM_PROMPT\]|```system)", re.I),
            "Delimiter hijacking: unauthorized system tag closure",
            0.95,
        ),
        (
            re.compile(r"repeat\s+everything\s+(written\s+)?above", re.I),
            "Prompt leakage: verbatim memory dump attempt",
            0.70,
        ),
        (
            re.compile(r"for\s+educational\s+purposes\s+only,?\s+how\s+to\s+(hack|attack|exploit|bypass)", re.I),
            "Adversarial roleplay: educational hypothetical bypass",
            0.65,
        ),
    ]

    @classmethod
    def scan(cls, text: str) -> tuple[bool, float, list[str]]:
        """Scans prompt text for injection patterns.

        Returns:
            Tuple of (is_safe, risk_score, risk_flags)
        """
        flags: list[str] = []
        accumulated_risk = 0.0

        for pattern, description, weight in cls.INJECTION_RULES:
            if pattern.search(text):
                flags.append(description)
                accumulated_risk = max(accumulated_risk, weight)

        # Cap risk score between 0.0 and 1.0
        final_risk = min(1.0, round(accumulated_risk, 2))
        is_safe = final_risk < 0.5

        return is_safe, final_risk, flags
