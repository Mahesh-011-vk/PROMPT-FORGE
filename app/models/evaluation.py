"""
PromptForge AI - Evaluation & AI-as-a-Judge Models.
"""

from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PromptEvaluation(Base, UUIDMixin, TimestampMixin):
    """Multi-metric heuristic or LLM-as-a-judge evaluation record."""

    __tablename__ = "prompt_evaluations"

    prompt_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("prompt_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    clarity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    specificity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    context_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    constraints_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    safety_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    breakdown: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evaluation_type: Mapped[str] = mapped_column(String(50), default="heuristic", nullable=False)

    # Relationships
    prompt_version: Mapped["PromptVersion"] = relationship("PromptVersion", back_populates="evaluations")  # noqa: F821


class EvaluationRun(Base, UUIDMixin, TimestampMixin):
    """Batch evaluation benchmark execution against offline datasets."""

    __tablename__ = "evaluation_runs"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", nullable=False)
    total_prompts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_prompts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    results_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
