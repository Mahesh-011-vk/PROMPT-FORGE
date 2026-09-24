"""
PromptForge AI - Data Engineering & Analytics Processing Engine.

Utilizes Pandas and NumPy for high-performance aggregations, percentile
distributions, time-series rollups, and cost projection models.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    CostForecast,
    LatencyPercentiles,
    ModalityBreakdownItem,
    ModelEfficiencyItem,
)


class AnalyticsEngine:
    """Analytical data transformation and metric calculation engine."""

    @staticmethod
    def process_events(events: list[dict[str, Any]]) -> AnalyticsSummaryResponse:
        """Transform a list of raw UsageEvent dictionaries into an executive summary."""
        if not events:
            # Return baseline empty report
            return AnalyticsSummaryResponse(
                total_events=0,
                total_tokens=0,
                total_cost=0.0,
                success_rate=100.0,
                avg_latency_ms=0.0,
                latency_percentiles=LatencyPercentiles(
                    p50_ms=0.0,
                    p90_ms=0.0,
                    p95_ms=0.0,
                    p99_ms=0.0,
                    min_ms=0.0,
                    max_ms=0.0,
                    avg_ms=0.0,
                ),
                modality_breakdown=[],
                model_efficiency=[],
                cost_forecast=CostForecast(
                    current_daily_burn=0.0,
                    projected_7_days=0.0,
                    projected_30_days=0.0,
                    daily_growth_rate=0.0,
                    top_contributing_modality="none",
                ),
            )

        df = pd.DataFrame(events)

        # Standardize missing columns
        for col in ["latency_ms", "tokens", "cost"]:
            if col not in df.columns:
                df[col] = 0
        if "status" not in df.columns:
            df["status"] = "SUCCESS"
        if "modality" not in df.columns:
            df["modality"] = "text"
        if "model_used" not in df.columns:
            df["model_used"] = "general"

        total_events = len(df)
        total_tokens = int(df["tokens"].sum())
        total_cost = round(float(df["cost"].sum()), 6)

        success_count = int((df["status"] == "SUCCESS").sum())
        success_rate = round((success_count / total_events) * 100.0, 2) if total_events > 0 else 100.0

        latencies = df["latency_ms"].to_numpy(dtype=float)
        avg_latency = round(float(np.mean(latencies)), 2)

        p50 = round(float(np.percentile(latencies, 50)), 2)
        p90 = round(float(np.percentile(latencies, 90)), 2)
        p95 = round(float(np.percentile(latencies, 95)), 2)
        p99 = round(float(np.percentile(latencies, 99)), 2)
        min_lat = round(float(np.min(latencies)), 2)
        max_lat = round(float(np.max(latencies)), 2)

        percentiles = LatencyPercentiles(
            p50_ms=p50,
            p90_ms=p90,
            p95_ms=p95,
            p99_ms=p99,
            min_ms=min_lat,
            max_ms=max_lat,
            avg_ms=avg_latency,
        )

        # Modality Breakdown
        modality_group = df.groupby("modality", as_index=False).agg(
            count=("latency_ms", "count"),
            tokens=("tokens", "sum"),
            cost=("cost", "sum"),
            avg_latency=("latency_ms", "mean"),
        )

        modality_items: list[ModalityBreakdownItem] = []
        for _, row in modality_group.iterrows():
            cnt = int(row["count"])
            pct = round((cnt / total_events) * 100.0, 2)
            modality_items.append(
                ModalityBreakdownItem(
                    modality=str(row["modality"]),
                    count=cnt,
                    tokens=int(row["tokens"]),
                    cost=round(float(row["cost"]), 6),
                    avg_latency_ms=round(float(row["avg_latency"]), 2),
                    percentage=pct,
                )
            )

        # Model Efficiency Breakdown
        model_group = df.groupby("model_used", as_index=False).agg(
            requests=("latency_ms", "count"),
            total_tokens=("tokens", "sum"),
            total_cost=("cost", "sum"),
            avg_latency=("latency_ms", "mean"),
        )

        model_items: list[ModelEfficiencyItem] = []
        for _, row in model_group.iterrows():
            reqs = int(row["requests"])
            toks = int(row["total_tokens"])
            model_items.append(
                ModelEfficiencyItem(
                    model_used=str(row["model_used"]),
                    requests=reqs,
                    total_tokens=toks,
                    avg_tokens_per_req=round(toks / reqs, 1) if reqs > 0 else 0.0,
                    total_cost=round(float(row["total_cost"]), 6),
                    avg_latency_ms=round(float(row["avg_latency"]), 2),
                )
            )

        # Top contributing modality by cost/count
        top_mod = (
            modality_group.sort_values(by="cost", ascending=False).iloc[0]["modality"]
            if not modality_group.empty
            else "general"
        )

        # Cost Forecast: approximate daily rate from observed data
        daily_burn = round(total_cost, 4) if total_cost > 0 else 0.05
        forecast = CostForecast(
            current_daily_burn=daily_burn,
            projected_7_days=round(daily_burn * 7.0 * 1.05, 4),
            projected_30_days=round(daily_burn * 30.0 * 1.15, 4),
            daily_growth_rate=5.0,
            top_contributing_modality=str(top_mod),
        )

        return AnalyticsSummaryResponse(
            total_events=total_events,
            total_tokens=total_tokens,
            total_cost=total_cost,
            success_rate=success_rate,
            avg_latency_ms=avg_latency,
            latency_percentiles=percentiles,
            modality_breakdown=modality_items,
            model_efficiency=model_items,
            cost_forecast=forecast,
        )

    @staticmethod
    def to_csv_string(events: list[dict[str, Any]]) -> str:
        """Convert telemetry event list to a clean CSV string using Pandas."""
        if not events:
            return "event_name,modality,category,model_used,latency_ms,tokens,cost,status,timestamp\n"
        df = pd.DataFrame(events)
        return df.to_csv(index=False)
