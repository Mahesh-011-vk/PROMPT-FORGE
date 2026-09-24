"""
PromptForge AI - Main Prompt Generation Engine Facade.

Integrates Intent Extraction, Slot Clarification, and Master Compilation
into a unified asynchronous generation pipeline.
"""

from app.core.exceptions import SafetyViolationException
from app.prompts.clarifier import smart_clarifier
from app.prompts.compiler import prompt_compiler
from app.prompts.intent_extractor import intent_extractor
from app.schemas.intent import SafetyClassification
from app.schemas.prompt import PromptGenerateRequest, PromptGenerationResult


class PromptEngine:
    """Enterprise Prompt Generation Pipeline Engine."""

    async def generate(self, request: PromptGenerateRequest) -> PromptGenerationResult:
        """
        Executes end-to-end prompt generation workflow from raw idea to multi-variant prompts.
        """
        # 1. Intent Extraction
        intent = intent_extractor.extract(
            raw_input=request.idea,
            modality_override=request.modality,
            category_override=request.category,
            audience_override=request.audience,
            target_model_override=request.target_model,
        )

        # 2. Safety Gate Check
        if intent.safety_classification == SafetyClassification.DISALLOWED:
            raise SafetyViolationException(
                message="The requested prompt violates safety and responsible AI policies.",
                reason="Prohibited harmful or dangerous content pattern detected.",
                safe_alternative="Try asking for creative, technical, or educational concepts.",
            )

        # 3. Missing Information & Clarification Slot Filling
        clarification = smart_clarifier.clarify(
            intent=intent,
            user_answers=request.user_answers,
        )

        # 4. Multi-Variant Compilation
        variants, explanation, suggestions, quality_score, score_breakdown = prompt_compiler.compile(
            intent=intent,
            auto_filled=clarification.auto_filled_values,
            target_model=request.target_model,
        )

        # 5. Assemble and Return Payload
        return PromptGenerationResult(
            original_input=request.idea,
            intent=intent,
            clarification=clarification,
            variants=variants,
            explanation=explanation,
            improvement_suggestions=suggestions,
            quality_score=quality_score,
            score_breakdown=score_breakdown,
        )


prompt_engine = PromptEngine()
