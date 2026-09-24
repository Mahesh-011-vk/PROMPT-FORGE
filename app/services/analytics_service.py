"""
PromptForge AI - Analytics Service.

Coordinates telemetry ingestion, event persistence in database,
and analytical aggregation reporting via AnalyticsEngine.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.engine import AnalyticsEngine
from app.models.analytics import UsageEvent
from app.schemas.analytics import AnalyticsSummaryResponse, UsageEventTrackRequest


class AnalyticsService:
    """Service layer managing analytics events and reporting."""

    @classmethod
    async def track_event(
        cls,
        db: AsyncSession,
        payload: UsageEventTrackRequest,
    ) -> dict[str, Any]:
        """Record a single telemetry event."""
        event = UsageEvent(
            event_name=payload.event_name,
            user_id=payload.user_id,
            project_id=payload.project_id,
            modality=payload.modality,
            category=payload.category,
            model_used=payload.model_used,
            latency_ms=payload.latency_ms,
            tokens=payload.tokens,
            cost=payload.cost,
            status=payload.status,
            metadata_=payload.metadata,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return {
            "id": event.id,
            "event_name": event.event_name,
            "status": event.status,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }

    @classmethod
    async def get_summary(
        cls,
        db: AsyncSession,
        days: int = 30,
    ) -> AnalyticsSummaryResponse:
        """Fetch usage events within the given day window and calculate aggregate analytics."""
        since = datetime.now(UTC) - timedelta(days=days)
        stmt = select(UsageEvent).where(UsageEvent.timestamp >= since)
        res = await db.execute(stmt)
        events = res.scalars().all()

        event_dicts = [
            {
                "event_name": e.event_name,
                "modality": e.modality or "text",
                "category": e.category or "general",
                "model_used": e.model_used or "general",
                "latency_ms": e.latency_ms,
                "tokens": e.tokens,
                "cost": e.cost,
                "status": e.status,
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
            }
            for e in events
        ]

        return AnalyticsEngine.process_events(event_dicts)

    @classmethod
    async def export_csv(
        cls,
        db: AsyncSession,
        limit: int = 5000,
    ) -> str:
        """Export events as CSV string."""
        stmt = select(UsageEvent).order_by(UsageEvent.timestamp.desc()).limit(limit)
        res = await db.execute(stmt)
        events = res.scalars().all()

        event_dicts = [
            {
                "id": e.id,
                "event_name": e.event_name,
                "modality": e.modality,
                "category": e.category,
                "model_used": e.model_used,
                "latency_ms": e.latency_ms,
                "tokens": e.tokens,
                "cost": e.cost,
                "status": e.status,
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
            }
            for e in events
        ]

        return AnalyticsEngine.to_csv_string(event_dicts)
