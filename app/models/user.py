"""
PromptForge AI - User and User Preferences Models.
"""

from typing import Any, Optional

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.constants import UserRole
from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User account entity with role-based access control."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum", native_enum=False),
        default=UserRole.USER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    preferences: Mapped[Optional["UserPreference"]] = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    prompts: Mapped[list["Prompt"]] = relationship(  # noqa: F821
        "Prompt",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list["Project"]] = relationship(  # noqa: F821
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserPreference(Base, UUIDMixin, TimestampMixin):
    """User prompt memory and personalized generation settings."""

    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    enable_memory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_modality: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    default_model: Mapped[str] = mapped_column(String(100), default="mock-forge-v1", nullable=False)
    custom_rules: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")
