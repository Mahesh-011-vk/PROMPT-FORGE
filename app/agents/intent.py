"""
PromptForge AI - Intent Agent.

Identifies domain persona, semantic categories, and tone requirements.
"""

from __future__ import annotations

import time
from app.agents.state import AgentState


class IntentAgent:
    """Specialized agent extracting persona, style, and tone nuances."""

    NAME = "IntentAgent"

    @classmethod
    async def run(cls, state: AgentState) -> None:
        """Extract fine-grained intent and target persona."""
        start = time.perf_counter()

        goal = state.goal.lower()

        # Resolve persona
        persona = state.persona
        if not persona or persona == "Expert AI Specialist":
            if state.modality == "code":
                persona = "Staff Software Architect & Security Auditor"
            elif state.modality == "image":
                persona = "Master Cinematographer & Concept Art Director"
            elif state.modality == "video":
                persona = "Cinematic Film Director & VFX Supervisor"
            elif any(w in goal for w in ["teach", "explain", "lesson", "kids", "school"]):
                persona = "Inspirational Socratic Educator"
            elif any(w in goal for w in ["ad", "copy", "landing", "campaign", "marketing"]):
                persona = "Senior Conversion Copywriter & Creative Strategist"

        state.persona = persona

        # Tone & style resolution
        if state.audience == "kids":
            tone = "playful, encouraging, highly visual, safe"
        elif state.modality == "code":
            tone = "authoritative, precise, bug-resilient, production-grade"
        elif state.modality in {"image", "video"}:
            tone = "atmospheric, photorealistic, visually descriptive"
        else:
            tone = "concise, professional, structured, actionable"

        state.intent = {
            "resolved_persona": state.persona,
            "tone": tone,
            "audience": state.audience,
            "output_format": "JSON/Markdown" if state.modality in {"text", "code"} else "Prompt string with parameters",
        }

        latency = int((time.perf_counter() - start) * 1000)
        state.add_trace(
            agent_name=cls.NAME,
            thought_process=f"Established persona: '{state.persona}' with tone '{tone}'.",
            output_summary=f"Persona: {state.persona} | Tone: {tone}",
            data=state.intent,
            latency_ms=max(latency, 2),
            tokens_used=50,
        )
