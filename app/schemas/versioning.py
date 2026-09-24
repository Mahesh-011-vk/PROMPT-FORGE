"""
PromptForge AI - Git-Like Prompt Version Control Schemas.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class VersionCommitRequest(BaseModel):
    """Payload to commit a new version of an existing prompt."""

    prompt_text: str = Field(..., min_length=5, description="Updated prompt content")
    negative_prompt: str | None = Field(None, description="Optional negative prompt")
    change_log: str = Field(..., min_length=2, max_length=500, description="Commit message describing changes")
    target_model: str = Field("general", description="Target model for this version")
    quality_score: float = Field(8.0, ge=0.0, le=10.0, description="Quality score for this version")
    variables: dict[str, Any] = Field(default_factory=dict)
    structured_spec: dict[str, Any] = Field(default_factory=dict)


class VersionSummary(BaseModel):
    """Snapshot of a version in commit history."""

    id: str
    prompt_id: str
    version_number: int
    prompt_text: str
    negative_prompt: str | None
    target_model: str
    quality_score: float
    change_log: str
    is_current: bool
    created_at: str | None


class DiffChunk(BaseModel):
    """An individual line or segment change in a diff."""

    type: Literal["added", "removed", "unchanged"]
    content: str
    line_number_from: int | None = None
    line_number_to: int | None = None


class VersionDiffResponse(BaseModel):
    """Comprehensive diff analysis between two prompt versions."""

    from_version: int
    to_version: int
    from_version_id: str
    to_version_id: str
    additions_count: int
    deletions_count: int
    unchanged_count: int
    similarity_ratio: float
    unified_diff: str
    chunks: list[DiffChunk]


class VersionRestoreResponse(BaseModel):
    """Result of restoring to a historical prompt version."""

    prompt_id: str
    restored_from_version: int
    new_version_number: int
    new_version_id: str
    message: str
