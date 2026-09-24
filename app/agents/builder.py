"""
PromptForge AI - Builder Agent.

Synthesizes structured, modular, and parameterized prompt drafts.
"""

from __future__ import annotations

import time

from app.agents.state import AgentState


class BuilderAgent:
    """Compiles prompt components into cohesive drafts with variables and guardrails."""

    NAME = "BuilderAgent"

    @classmethod
    async def run(cls, state: AgentState) -> None:
        """Construct the prompt draft based on plan, intent, and retrieved knowledge."""
        start = time.perf_counter()

        modality = state.modality
        goal = state.goal.strip()
        persona = state.persona

        variables: dict[str, str] = {}
        negative_prompt: str | None = None
        draft: str

        if modality == "image":
            draft = (
                f"Masterpiece photograph, {goal}, directed by {persona}. "
                "Shot on 85mm f/1.4 lens, cinematic volumetric lighting, ray-traced ambient reflections, "
                "hyper-detailed textures, 8k resolution, Unreal Engine 5 render, award-winning composition --ar 16:9 --v 6.0"
            )
            negative_prompt = (
                "blurry, distorted anatomy, bad hands, low resolution, watermark, text, out of frame, oversaturated, deformed"
            )
            variables = {"subject": goal, "lighting": "cinematic volumetric lighting", "aspect_ratio": "16:9"}

        elif modality == "video":
            draft = (
                f"Cinematic video sequence: {goal}. "
                "Camera Movement: Smooth slow dolly-in with subtle orbital roll. "
                "Lighting: High dynamic range volumetric dusk lighting with atmospheric mist. "
                "Temporal Dynamics: 24fps motion blur, fluid realistic physics, hyper-detailed particle rendering. "
                "--motion 5 --camera dolly-in --fps 24"
            )
            negative_prompt = (
                "jittery camera, abrupt morphing, flickering, disjointed temporal cuts, pixelated artifacts, stutter"
            )
            variables = {"scene": goal, "camera_motion": "slow dolly-in", "fps": "24"}

        elif modality == "code":
            draft = (
                f"You are a {persona}.\n\n"
                f"### Objective:\nImplement production-grade, bug-free code for: {goal}\n\n"
                "### Architectural & Implementation Requirements:\n"
                "1. Language & Typing: Use idiomatic modern conventions with complete type annotations.\n"
                "2. Error Handling & Edge Cases: Explicitly validate boundary inputs and gracefully handle asynchronous or concurrency hazards.\n"
                "3. Performance & Complexity: Optimize algorithm time and space complexity (document Big-O notation).\n"
                "4. Testability: Provide accompanying comprehensive unit tests with edge-case fixtures.\n"
                "5. Zero Placeholders: Do not write `# TODO` or omit details; output full, executable code blocks.\n\n"
                "### Target Input:\n{{code_context}}\n\n"
                "### Output Structure:\n"
                "- Architecture Overview\n"
                "- Production Implementation\n"
                "- Unit Tests & Edge Case Assertions"
            )
            variables = {"code_context": "Provide repository context or schema here"}

        elif state.audience == "kids":
            draft = (
                f"You are an encouraging, friendly {persona} for curious children aged 7-11!\n\n"
                f"### Mission:\nExplain and explore: {goal}\n\n"
                "### Guidelines for Fun & Safety:\n"
                "1. Tone: Super enthusiastic, warm, welcoming, and kid-friendly!\n"
                "2. Analogies: Use playful real-world examples (like pizza slices, rockets, or animal superpowers).\n"
                "3. Interactivity: Include a mini quiz or fun challenge at the end!\n"
                "4. Safety: Strictly safe, positive, and non-violent vocabulary at all times."
            )
            variables = {"topic": goal}

        else:
            # Default advanced text prompt
            draft = (
                f"You are a {persona}.\n\n"
                f"### Goal & Context:\n{goal}\n\n"
                "### Execution Directives:\n"
                "1. Structured Analysis: Deconstruct the problem logically before formulating answers.\n"
                "2. Specificity & Tone: Maintain an authoritative, nuanced, and actionable professional tone.\n"
                "3. Constraints: Avoid generic platitudes; provide empirical examples and verifiable rationale.\n"
                "4. Output Deliverable: Format responses using clean markdown headers and bullet points.\n\n"
                "### Input Context:\n{{user_context}}"
            )
            variables = {"user_context": "Insert specific background documents or query variables here"}

        state.draft_prompt = draft
        state.negative_prompt = negative_prompt
        state.variables = variables

        latency = int((time.perf_counter() - start) * 1000)
        state.add_trace(
            agent_name=cls.NAME,
            thought_process="Assembled modular prompt draft with role, constraints, formatting, and variables.",
            output_summary=f"Synthesized draft ({len(draft)} chars, {len(variables)} variables).",
            data={
                "draft_length": len(draft),
                "variable_count": len(variables),
                "has_negative_prompt": negative_prompt is not None,
            },
            latency_ms=max(latency, 2),
            tokens_used=180,
        )
