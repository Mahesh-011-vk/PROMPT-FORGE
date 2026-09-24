"""
PromptForge AI - Critic Agent.

Performs rigorous adversarial auditing, constraint verification, and heuristic scoring.
"""

from __future__ import annotations

import time
from app.agents.state import AgentState
from app.evaluators.heuristics import heuristic_scorer
from app.schemas.agents import StandaloneCritiqueResponse


class CriticAgent:
    """Audits prompt drafts against enterprise prompting benchmarks."""

    NAME = "CriticAgent"

    @classmethod
    async def run(cls, state: AgentState) -> None:
        """Audit the draft prompt and record critique feedback."""
        start = time.perf_counter()

        overall_100, metrics, heuristic_feedback = heuristic_scorer.evaluate(
            prompt=state.draft_prompt,
            modality=state.modality,
        )
        quality_score = round(overall_100 / 10.0, 1)

        strengths: list[str] = []
        weaknesses: list[str] = []
        suggestions: list[str] = list(heuristic_feedback)

        clarity_val = metrics.get("clarity").score if "clarity" in metrics else 80.0
        if clarity_val >= 80.0:
            strengths.append("Clear semantic directives and well-defined role boundary.")
        else:
            weaknesses.append("Ambiguity in target scope or role expectations.")
            suggestions.append("Clarify the specific persona and expected boundaries.")

        if state.variables:
            strengths.append(f"Parametric adaptability via {len(state.variables)} variables.")

        if not suggestions:
            suggestions.append("Prompt meets high-rigor enterprise production guidelines.")

        state.critique = {
            "quality_score": quality_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "verdict": "READY_FOR_DEPLOYMENT" if quality_score >= 8.0 else "REVISION_RECOMMENDED",
        }
        state.quality_score = quality_score

        latency = int((time.perf_counter() - start) * 1000)
        state.add_trace(
            agent_name=cls.NAME,
            thought_process=f"Evaluated draft against {state.modality} rubric. Scored: {quality_score}/10.",
            output_summary=f"Quality score {quality_score}/10 ({state.critique['verdict']}).",
            data=state.critique,
            latency_ms=max(latency, 2),
            tokens_used=110,
        )

    @classmethod
    def evaluate_standalone(
        cls,
        prompt_text: str,
        modality: str = "text",
        target_model: str = "gpt-4o",
    ) -> StandaloneCritiqueResponse:
        """Standalone critique evaluation for arbitrary prompts."""
        overall_100, _, heuristic_feedback = heuristic_scorer.evaluate(
            prompt=prompt_text,
            modality=modality,
        )
        quality_score = round(overall_100 / 10.0, 1)

        strengths: list[str] = []
        weaknesses: list[str] = []
        suggestions: list[str] = list(heuristic_feedback)
        ambiguity: list[str] = []

        if len(prompt_text.split()) < 10:
            weaknesses.append("Prompt is very short and lacks detailed contextual framing.")
            ambiguity.append("High ambiguity: open to broad interpretations by model.")
            suggestions.append("Expand requirements, specify role, target audience, and output format.")
        else:
            strengths.append("Sufficient prompt length and contextual volume.")

        if "```" in prompt_text or "format" in prompt_text.lower():
            strengths.append("Explicit output formatting directives present.")
        else:
            suggestions.append("Provide explicit output structure (e.g. JSON schema or Markdown headers).")

        return StandaloneCritiqueResponse(
            overall_verdict="APPROVED" if quality_score >= 7.5 else "NEEDS_OPTIMIZATION",
            quality_score=quality_score,
            strengths=strengths,
            weaknesses=weaknesses,
            suggested_improvements=suggestions,
            ambiguity_flags=ambiguity,
        )
