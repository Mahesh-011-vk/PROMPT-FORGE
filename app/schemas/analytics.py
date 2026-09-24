"""
PromptForge AI - Data Engineering & Analytics Schemas.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UsageEventTrackRequest(BaseModel):
    """Payload to log telemetry usage events."""

    event_name: str = Field(..., description="Event action (e.g., prompt.generate, prompt.optimize)")
    user_id: str | None = None
    project_id: str | None = None
    modality: str | None = Field("text", description="Modality involved")
    category: str | None = Field("general", description="Category or domain")
    model_used: str | None = Field("mock-model", description="Model name or provider")
    latency_ms: int = Field(0, ge=0, description="Latency in milliseconds")
    tokens: int = Field(0, ge=0, description="Token consumption count")
    cost: float = Field(0.0, ge=0.0, description="Estimated dollar cost")
    status: str = Field("SUCCESS", description="SUCCESS or ERROR")
    metadata: dict[str, Any] = Field(default_factory=dict)


class LatencyPercentiles(BaseModel):
    """Percentile distribution of platform latencies."""

    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    min_ms: float
    max_ms: float
    avg_ms: float


class ModalityBreakdownItem(BaseModel):
    """Aggregated metrics per modality."""

    modality: str
    count: int
    tokens: int
    cost: float
    avg_latency_ms: float
    percentage: float


class ModelEfficiencyItem(BaseModel):
    """Performance and cost efficiency per model."""

    model_used: str
    requests: int
    total_tokens: int
    avg_tokens_per_req: float
    total_cost: float
    avg_latency_ms: float


class CostForecast(BaseModel):
    """Extrapolated cost forecasting based on current usage velocity."""

    current_daily_burn: float
    projected_7_days: float
    projected_30_days: float
    daily_growth_rate: float
    top_contributing_modality: str


class AnalyticsSummaryResponse(BaseModel):
    """Comprehensive executive analytics overview."""

    total_events: int
    total_tokens: int
    total_cost: float
    success_rate: float
    avg_latency_ms: float
    latency_percentiles: LatencyPercentiles
    modality_breakdown: list[ModalityBreakdownItem]
    model_efficiency: list[ModelEfficiencyItem]
    cost_forecast: CostForecast
