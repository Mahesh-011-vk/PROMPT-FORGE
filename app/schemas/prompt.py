"""
PromptForge AI - Prompt Generation and Execution Schemas.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.config.constants import AudienceCategory, Modality
from app.schemas.intent import ClarificationResult, PromptIntent


class ImagePromptSpec(BaseModel):
    """Granular parameters for photorealistic or artistic image prompt generation."""

    subject: str = Field(..., description="Main visual subject")
    environment: str = Field("", description="Background, setting, or scenery")
    composition: str = Field("", description="Rule of thirds, centered, wide view, close up")
    camera: str = Field("", description="ARRI Alexa, Hasselblad H6D-100c, Canon EOS R5")
    lens: str = Field("", description="35mm anamorphic, 85mm f/1.4 portrait lens")
    lighting: str = Field("", description="Volumetric rays, golden hour, neon rim light, soft diffuse")
    color_palette: str = Field("", description="Duotone, muted pastel, Cyberpunk neon, warm amber")
    style: str = Field("", description="Photorealistic, cinematic film still, octane render, anime")
    materials: str = Field("", description="Brushed titanium, wet asphalt, velvet, weathered marble")
    textures: str = Field("", description="Intricate skin pores, rain droplets, subtle film grain")
    mood: str = Field("", description="Brooding, euphoric, serene, ominous, epic")
    time_of_day: str = Field("", description="Midnight, blue hour, twilight, overcast noon")
    weather: str = Field("", description="Gentle mist, heavy rain, clear sky, sandstorm")
    depth_of_field: str = Field("", description="Shallow depth of field, f/1.8 bokeh, deep focus")
    quality: str = Field("8k resolution, photorealistic, masterpiece", description="Fidelity tags")
    negative_prompt: str = Field("blurry, distorted, oversaturated, deformed, text, watermark, bad anatomy", description="Excluded visual elements")


class VideoPromptSpec(BaseModel):
    """Detailed parameters for AI video models (Runway Gen-3, OpenAI Sora, Kling)."""

    scene: str = Field(..., description="Core setting and context of the sequence")
    character: str = Field("", description="Actor, subject, or focal character")
    action: str = Field(..., description="Explicit movement or physical action occurring")
    environment: str = Field("", description="Dynamic environmental elements")
    camera_movement: str = Field("", description="Slow forward dolly, drone sweep, whip pan, tracking shot")
    camera_angle: str = Field("", description="Eye-level, low-angle hero perspective, bird's eye")
    lens: str = Field("", description="Wide angle, telephoto, 50mm cinematic prime")
    lighting: str = Field("", description="Atmospheric lighting, volumetric fog, dynamic lens flare")
    motion_speed: str = Field("", description="Slow motion 60fps, real-time, time-lapse, high-speed")
    visual_style: str = Field("", description="35mm film grain, 70mm IMAX aesthetic, documentarian")
    audio_description: str = Field("", description="Ambient room tone, sound effects, musical motif")
    dialogue: str = Field("", description="Spoken dialogue or voiceover if any")
    timing: str = Field("5 seconds", description="Duration or pacing of the clip")
    transitions: str = Field("", description="Cross-dissolve, match cut, hard cut")
    negative_constraints: str = Field("jitter, morphing, jerky motion, unrealistic physics, flickering", description="Artifact constraints")


class PromptVariant(BaseModel):
    """Individual prompt generation variant."""

    variant_type: str = Field(..., description="basic, advanced, expert, model_specific, structured_json")
    title: str = Field(..., description="Descriptive variant name")
    prompt_text: str = Field(..., description="The complete generated prompt text")
    negative_prompt: str | None = Field(default=None, description="Negative prompt if applicable")
    structured_json: dict[str, Any] | None = Field(default=None, description="Machine-readable specification")
    variables: dict[str, str] = Field(default_factory=dict, description="Customizable template variables")
    recommended_settings: dict[str, Any] = Field(default_factory=dict, description="Recommended model parameters")


class PromptExplanation(BaseModel):
    """Comprehensive AI explanation of prompt engineering decisions."""

    summary: str = Field(..., description="What this prompt accomplishes")
    why_added: list[str] = Field(default_factory=list, description="Rationale for specific descriptive tokens")
    customization_points: list[str] = Field(default_factory=list, description="Variables or slots the user can tweak")
    expected_outputs: str = Field(..., description="Anticipated behavior and characteristics of model output")
    potential_weaknesses: list[str] = Field(default_factory=list, description="Common edge cases or model limitations to watch for")


class PromptGenerateRequest(BaseModel):
    """User input for generating a prompt."""

    idea: str = Field(..., description="Initial raw concept or requirement from user")
    modality: Modality | None = Field(default=None, description="Override detected modality")
    category: str | None = Field(default=None, description="Override taxonomy category")
    audience: AudienceCategory | None = Field(default=None, description="Target audience tier")
    target_model: str = Field(default="default", description="Specific model (e.g., midjourney, gpt-4o, claude, runway)")
    auto_clarify: bool = Field(default=True, description="Automatically fill missing slots with intelligent defaults")
    user_answers: dict[str, str] = Field(default_factory=dict, description="Explicit answers to clarification questions")


class PromptGenerationResult(BaseModel):
    """Full payload returned from the Prompt Generation Engine."""

    original_input: str
    intent: PromptIntent
    clarification: ClarificationResult
    variants: dict[str, PromptVariant]
    explanation: PromptExplanation
    improvement_suggestions: list[str]
    quality_score: float = Field(..., description="Overall heuristic prompt score (0-100)")
    score_breakdown: dict[str, float] = Field(default_factory=dict)
