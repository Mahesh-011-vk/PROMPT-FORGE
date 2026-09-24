"""
PromptForge AI - Optimizer, Repair, and Translation Schemas.
"""

from pydantic import BaseModel, Field

from app.config.constants import Modality


class PromptOptimizeRequest(BaseModel):
    """Payload for optimizing an existing sub-optimal prompt."""

    prompt: str = Field(..., description="The user's existing prompt text")
    modality: Modality | None = Field(default=None, description="Modality hint")
    target_model: str = Field(default="default", description="Target model format")
    preserve_intent: bool = Field(default=True, description="Strictly preserve original core subject")


class WeaknessAnalysis(BaseModel):
    """Analysis of why the original prompt was deficient."""

    ambiguity_level: str = Field(..., description="high, medium, low")
    weaknesses_detected: list[str] = Field(default_factory=list, description="Specific flaws identified")
    missing_dimensions: list[str] = Field(default_factory=list, description="Missing essential parameters")


class PromptOptimizeResponse(BaseModel):
    """Before/after prompt optimization artifact."""

    original_prompt: str
    optimized_prompt: str
    weakness_analysis: WeaknessAnalysis
    why_improved: list[str]
    diff_summary: str
    score_before: float = Field(..., description="Estimated quality score of original (0-100)")
    score_after: float = Field(..., description="Estimated quality score of optimized prompt (0-100)")
    suggested_model: str


class PromptRepairRequest(BaseModel):
    """Payload for repairing highly ambiguous or broken prompts."""

    prompt: str = Field(..., description="Broken, vague, or fragmented prompt (e.g., 'make a good website')")
    context: str | None = Field(default=None, description="Optional extra business/technical context")


class PromptRepairResponse(BaseModel):
    """Deconstructed and repaired prompt architecture."""

    original_prompt: str
    identified_ambiguity: list[str]
    objective: str
    audience: str
    technology_stack: str
    design_system: str
    functional_requirements: list[str]
    explicit_constraints: list[str]
    output_format: str
    repaired_prompt: str


class PromptTranslateRequest(BaseModel):
    """Payload for translating prompts while preserving prompt engineering syntax."""

    prompt: str = Field(..., description="Prompt text to translate")
    target_language: str = Field(..., description="Target language (e.g., Spanish, Japanese, German, French)")
    preserve_tags: bool = Field(default=True, description="Preserve parameters like --ar 16:9, XML tags, and code blocks")


class PromptTranslateResponse(BaseModel):
    """Translated prompt result."""

    original_prompt: str
    translated_prompt: str
    target_language: str
    preserved_elements: list[str]
