"""
PromptForge AI - Intent and Clarification Schemas.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.config.constants import AudienceCategory, Modality, SafetyClassification


class PromptIntent(BaseModel):
    """Structured extraction of user intent and prompt engineering requirements."""

    objective: str = Field(..., description="Primary goal or task the user wants to accomplish")
    modality: Modality = Field(default=Modality.TEXT, description="Detected or requested modality")
    category: str = Field(default="general", description="Taxonomy category slug")
    subcategories: list[str] = Field(default_factory=list, description="Specific sub-domains")
    audience: AudienceCategory = Field(default=AudienceCategory.PROFESSIONALS, description="Target reader or user audience")
    subject: str = Field(..., description="Central topic, entity, or actor")
    environment: str | None = Field(default=None, description="Setting, backdrop, or domain context")
    style: str | None = Field(default=None, description="Aesthetic, writing style, or artistic movement")
    tone: str | None = Field(default=None, description="Tone of voice (e.g. cinematic, authoritative, whimsical)")
    constraints: list[str] = Field(default_factory=list, description="Negative constraints, boundaries, or restrictions")
    output_format: str = Field(default="markdown", description="Requested output format (e.g. JSON, code, prose, image tags)")
    target_model: str = Field(default="default", description="Specific model targeted (e.g. midjourney, gpt-4o, claude)")
    language: str = Field(default="English", description="Target human language")
    complexity: str = Field(default="intermediate", description="beginner, intermediate, advanced, expert")
    safety_classification: SafetyClassification = Field(default=SafetyClassification.SAFE)
    technical_parameters: dict[str, Any] = Field(default_factory=dict, description="Model-specific parameters like aspect ratio, temperature")


class ClarificationQuestion(BaseModel):
    """High-value question to disambiguate missing essential details."""

    slot_name: str = Field(..., description="Target attribute name (e.g. camera, duration, style)")
    question: str = Field(..., description="Concise human-friendly question")
    suggested_options: list[str] = Field(default_factory=list, description="Quick-pick suggestions for the user")
    inferred_default: str = Field(..., description="Reasonable AI default if user selects auto-fill")
    importance: str = Field(default="high", description="high, medium, low")


class ClarificationResult(BaseModel):
    """Collection of detected missing slots and resolution questions."""

    has_missing_slots: bool = Field(default=False)
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    auto_filled_values: dict[str, str] = Field(default_factory=dict)
