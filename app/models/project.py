"""
PromptForge AI - Project Workspace Model.
"""

from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Project(Base, UUIDMixin, TimestampMixin):
    """Collaborative workspace for grouping prompts, templates, and evaluations."""

    __tablename__ = "projects"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")  # noqa: F821
    prompts: Mapped[list["Prompt"]] = relationship(  # noqa: F821
        "Prompt",
        back_populates="project",
        cascade="all, delete-orphan",
    )
