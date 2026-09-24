"""
PromptForge AI - Data Engineering & Analytics API Endpoints.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    CostForecast,
    LatencyPercentiles,
    ModalityBreakdownItem,
    UsageEventTrackRequest,
)
from app.schemas.common import ResponseEnvelope
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Data Analytics & Telemetry"])


@router.post("/events")
async def track_event(
    payload: UsageEventTrackRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict[str, Any]]:
    """Record platform usage telemetry (generation, optimization, token consumption)."""
    tracked = await AnalyticsService.track_event(db=db, payload=payload)
    return ResponseEnvelope(
        data=tracked,
        message="Telemetry event recorded",
    )


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[AnalyticsSummaryResponse]:
    """Retrieve complete platform metrics, percentiles, model efficiency, and cost forecast."""
    summary = await AnalyticsService.get_summary(db=db, days=days)
    return ResponseEnvelope(data=summary)


@router.get("/modalities")
async def get_modality_breakdown(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[ModalityBreakdownItem]]:
    """Retrieve usage, cost, and volume breakdown aggregated by modality."""
    summary = await AnalyticsService.get_summary(db=db, days=days)
    return ResponseEnvelope(data=summary.modality_breakdown)


@router.get("/latency")
async def get_latency_percentiles(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[LatencyPercentiles]:
    """Retrieve p50, p90, p95, and p99 latency distributions."""
    summary = await AnalyticsService.get_summary(db=db, days=days)
    return ResponseEnvelope(data=summary.latency_percentiles)


@router.get("/forecast")
async def get_cost_forecast(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[CostForecast]:
    """Retrieve projected costs and token burn rate forecast."""
    summary = await AnalyticsService.get_summary(db=db, days=days)
    return ResponseEnvelope(data=summary.cost_forecast)


@router.get("/export")
async def export_telemetry_csv(
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download telemetry events as a standard CSV file."""
    csv_str = await AnalyticsService.export_csv(db=db, limit=limit)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=promptforge_telemetry.csv"},
    )
