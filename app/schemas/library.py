"""
PromptForge AI - Prompt Library & Template Schemas.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TemplateCreateRequest(BaseModel):
    """Payload to create a new reusable prompt template."""

    title: str = Field(..., min_length=3, max_length=200, json_schema_extra={"example": "Cinematic Character Portrait"})
    description: str | None = Field(None, json_schema_extra={"example": "Template for ultra-detailed Midjourney character portraits"})
    modality: str = Field("image", json_schema_extra={"example": "image"})
    category: str = Field("creative", json_schema_extra={"example": "creative"})
    template_str: str = Field(
        ...,
        min_length=5,
        json_schema_extra={"example": "A cinematic portrait of a {{character_role}}, {{lighting_style | default: golden hour}} lighting, 8k resolution."},
    )
    default_variables: dict[str, Any] = Field(default_factory=dict)
    is_system: bool = Field(False)


class TemplateRenderRequest(BaseModel):
    """Payload to render a template with variable substitutions."""

    template_id: str | None = Field(None, description="Optional ID of existing database template")
    template_str: str | None = Field(None, description="Direct template string if not using template_id")
    variables: dict[str, Any] = Field(default_factory=dict, description="Key-value pairs for substitution")
    strict: bool = Field(False, description="Fail if required variables are missing")


class TemplateRenderResponse(BaseModel):
    """Result of template variable rendering."""

    rendered_text: str
    used_variables: dict[str, Any]
    missing_variables: list[str]
    success: bool
    error_message: str | None = None


class TemplateExtractRequest(BaseModel):
    """Payload to extract variables from a template string."""

    template_str: str


class TemplateVariableInfo(BaseModel):
    """Information about an extracted variable."""

    name: str
    required: bool
    default_value: str | None = None
    filters: list[str] = Field(default_factory=list)


class TemplateExtractResponse(BaseModel):
    """Extracted variables metadata."""

    variables: list[TemplateVariableInfo]
    count: int


class PromptCreateRequest(BaseModel):
    """Payload to create a new prompt entry in the library."""

    title: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Cyberpunk Street Food Vendor"})
    raw_input: str = Field(..., min_length=2, json_schema_extra={"example": "Street food vendor in neo tokyo rain"})
    prompt_text: str = Field(..., min_length=5, json_schema_extra={"example": "Masterpiece, a cyberpunk noodle vendor..."})
    negative_prompt: str | None = Field(None, json_schema_extra={"example": "blurry, low quality"})
    modality: str = Field("image", json_schema_extra={"example": "image"})
    category: str = Field("concept_art", json_schema_extra={"example": "concept_art"})
    audience: str = Field("general", json_schema_extra={"example": "general"})
    target_model: str = Field("midjourney-v6", json_schema_extra={"example": "midjourney-v6"})
    tags: list[str] = Field(default_factory=list, json_schema_extra={"example": ["cyberpunk", "tokyo", "street"]})
    is_favorite: bool = Field(False)
    quality_score: float = Field(8.5, ge=0.0, le=10.0)
    variables: dict[str, Any] = Field(default_factory=dict)
    structured_spec: dict[str, Any] = Field(default_factory=dict)
    project_id: str | None = None
    user_id: str | None = None


class PromptUpdateRequest(BaseModel):
    """Payload to update an existing prompt's metadata."""

    title: str | None = Field(None, min_length=2, max_length=255)
    category: str | None = None
    audience: str | None = None
    tags: list[str] | None = None
    is_favorite: bool | None = None


class PromptVersionSummary(BaseModel):
    """Summary of a prompt version."""

    id: str
    version_number: int
    prompt_text: str
    negative_prompt: str | None = None
    target_model: str
    quality_score: float
    change_log: str
    created_at: str | None = None


class PromptDetailResponse(BaseModel):
    """Detailed prompt information including versions."""

    id: str
    title: str
    raw_input: str
    modality: str
    category: str
    audience: str
    is_favorite: bool
    tags: list[str]
    current_version_id: str | None = None
    current_prompt_text: str | None = None
    quality_score: float = 0.0
    versions: list[PromptVersionSummary] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


class PromptExportRequest(BaseModel):
    """Request to export library prompts."""

    format: Literal["json", "csv", "markdown", "yaml"] = Field("json")
    modality: str | None = None
    category: str | None = None
    tag: str | None = None
    only_favorites: bool = False


class PromptExportResponse(BaseModel):
    """Exported content response."""

    format: str
    content: str
    prompt_count: int
    filename: str


class PromptImportItem(BaseModel):
    """Individual prompt to import."""

    title: str
    raw_input: str
    prompt_text: str
    modality: str = "text"
    category: str = "general"
    audience: str = "general"
    target_model: str = "general"
    tags: list[str] = Field(default_factory=list)
    quality_score: float = 8.0


class PromptImportRequest(BaseModel):
    """Payload to batch import prompts."""

    prompts: list[PromptImportItem]


class PromptImportResponse(BaseModel):
    """Summary of import results."""

    imported_count: int
    created_ids: list[str]
    errors: list[str] = Field(default_factory=list)
