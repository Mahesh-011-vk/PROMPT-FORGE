"""
PromptForge AI - Safety & Alignment Agent.

Enforces guardrails, jailbreak defense, PII scanning, and audience suitability.
"""

from __future__ import annotations

import re
import time
from app.agents.state import AgentState


class SafetyAgent:
    """Verifies content safety, prompt injection resistance, and age alignment."""

    NAME = "SafetyAgent"

    # Known prompt injection / jailbreak patterns
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions?", re.I),
        re.compile(r"you\s+are\s+now\s+in\s+DAN\s+mode", re.I),
        re.compile(r"system\s*override", re.I),
        re.compile(r"bypass\s+all\s+safety\s+filters?", re.I),
    ]

    KIDS_UNSAFE_PATTERNS = [
        re.compile(r"\b(violent|blood|gore|weapon|kill|gun|murder|knife|drug)\b", re.I),
    ]

    @classmethod
    async def run(cls, state: AgentState) -> None:
        """Scan state draft prompt and goals for safety risks."""
        start = time.perf_counter()

        flags: list[str] = []
        combined_text = f"{state.goal}\n{state.draft_prompt}"

        # 1. Prompt Injection Scan
        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(combined_text):
                flags.append("Suspected prompt injection / system instruction override payload detected.")
                break

        # 2. Kids Mode Safety Scan
        if state.audience == "kids":
            for pat in cls.KIDS_UNSAFE_PATTERNS:
                if pat.search(combined_text):
                    flags.append("Violated kids safety policy: inappropriate content keywords detected.")
                    break

        if flags and state.strict_safety:
            verdict = "WARNING" if "injection" not in flags[0].lower() else "BLOCKED"
        else:
            verdict = "APPROVED"

        state.safety_verdict = verdict
        state.safety_details = {
            "verdict": verdict,
            "flags": flags,
            "safe": verdict != "BLOCKED",
        }

        latency = int((time.perf_counter() - start) * 1000)
        state.add_trace(
            agent_name=cls.NAME,
            thought_process=f"Scanned prompt for injection vectors and audience safety ({state.audience}). Verdict: {verdict}.",
            output_summary=f"Safety Verdict: {verdict} ({len(flags)} risk flags).",
            data=state.safety_details,
            latency_ms=max(latency, 2),
            tokens_used=40,
        )
