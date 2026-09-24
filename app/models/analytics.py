"""
PromptForge AI - Analytics and Audit Logging Models.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, utc_now


class UsageEvent(Base, UUIDMixin):
    """Granular platform event logged for data analytics, costs, and token monitoring."""

    __tablename__ = "usage_events"

    event_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    modality: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS", nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
        nullable=False,
    )


class AuditLog(Base, UUIDMixin):
    """Security audit trail for regulatory compliance and access tracking."""

    __tablename__ = "audit_logs"

    user_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(200), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
        nullable=False,
    )
