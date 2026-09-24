"""
PromptForge AI - Planner Agent.

Deconstructs prompt engineering goals into actionable modular specifications.
"""

from __future__ import annotations

import time

from app.agents.state import AgentState


class PlannerAgent:
    """Decomposes the raw user request into structural prompting requirements."""

    NAME = "PlannerAgent"

    @classmethod
    async def run(cls, state: AgentState) -> None:
        """Analyze user goal and formulate engineering plan."""
        start = time.perf_counter()

        goal_lower = state.goal.lower()
        sub_goals: list[str] = [
            "Deconstruct target persona and domain objectives",
            "Retrieve relevant few-shot exemplars and formatting standards",
            "Synthesize modular prompt draft with variable boundaries",
            "Perform adversarial critique and constraint verification",
            "Validate safety, guardrails, and alignment",
        ]

        # Determine implied modalities if not forced
        detected_modality = state.modality
        if not detected_modality or detected_modality == "text":
            if any(w in goal_lower for w in ["photo", "illustration", "painting", "render", "image", "portrait"]):
                detected_modality = "image"
            elif any(w in goal_lower for w in ["video", "animation", "motion", "clip", "cinematics"]):
                detected_modality = "video"
            elif any(w in goal_lower for w in ["function", "class", "code", "algorithm", "python", "typescript", "bug"]):
                detected_modality = "code"

        state.modality = detected_modality or "text"

        state.plan = {
            "sub_goals": sub_goals,
            "target_modality": state.modality,
            "complexity_level": "advanced" if len(state.goal.split()) > 10 else "standard",
            "requires_few_shot": state.modality in {"code", "text"},
            "negative_prompt_required": state.modality in {"image", "video"},
        }

        latency = int((time.perf_counter() - start) * 1000)
        state.add_trace(
            agent_name=cls.NAME,
            thought_process=f"Goal '{state.goal[:60]}...' analyzed. Resolved modality: {state.modality}.",
            output_summary=f"Formulated 5-stage synthesis plan for {state.modality} modality.",
            data=state.plan,
            latency_ms=max(latency, 2),
            tokens_used=65,
        )
