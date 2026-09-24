"""
PromptForge AI - Prompt, Version, Category, and Template Models.
"""

from typing import Any, Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PromptCategory(Base, UUIDMixin, TimestampMixin):
    """Hierarchical category taxonomy for organizing prompts."""

    __tablename__ = "prompt_categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    modality: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("prompt_categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    children: Mapped[list["PromptCategory"]] = relationship("PromptCategory")


class Prompt(Base, UUIDMixin, TimestampMixin):
    """Core Prompt entity representing a prompt concept and its versions."""

    __tablename__ = "prompts"

    project_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    modality: Mapped[str] = mapped_column(String(50), default="text", index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="general", index=True, nullable=False)
    audience: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    current_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="prompts")  # noqa: F821
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="prompts")  # noqa: F821
    versions: Mapped[list["PromptVersion"]] = relationship(
        "PromptVersion",
        back_populates="prompt",
        cascade="all, delete-orphan",
        order_by="PromptVersion.version_number",
    )


class PromptVersion(Base, UUIDMixin, TimestampMixin):
    """Git-like immutable version snapshot of a generated or edited prompt."""

    __tablename__ = "prompt_versions"

    prompt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("prompts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_spec: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    variables: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    target_model: Mapped[str] = mapped_column(String(100), default="general", nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    change_log: Mapped[str] = mapped_column(String(500), default="Initial generation", nullable=False)
    author_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Relationships
    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="versions")
    evaluations: Mapped[list["PromptEvaluation"]] = relationship(  # noqa: F821
        "PromptEvaluation",
        back_populates="prompt_version",
        cascade="all, delete-orphan",
    )


class PromptTemplate(Base, UUIDMixin, TimestampMixin):
    """Reusable prompt template with slot parameters (e.g., {{subject}}, {{style}})."""

    __tablename__ = "prompt_templates"

    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    modality: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    template_str: Mapped[str] = mapped_column(Text, nullable=False)
    default_variables: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
