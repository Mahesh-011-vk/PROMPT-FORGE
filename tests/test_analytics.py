"""
Tests for Phase 14: Data Engineering & Analytics Pipeline.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.analytics.engine import AnalyticsEngine
from app.main import app


def test_analytics_engine_empty_fallback():
    """Verify analytics engine returns graceful default response when no events exist."""
    summary = AnalyticsEngine.process_events([])
    assert summary.total_events == 0
    assert summary.total_tokens == 0
    assert summary.total_cost == 0.0
    assert summary.latency_percentiles.p50_ms == 0.0


def test_analytics_engine_with_sample_telemetry():
    """Verify pandas percentiles, modality grouping, and cost projections."""
    sample_events = [
        {"modality": "image", "model_used": "midjourney-v6", "latency_ms": 120, "tokens": 40, "cost": 0.002, "status": "SUCCESS"},
        {"modality": "image", "model_used": "midjourney-v6", "latency_ms": 180, "tokens": 60, "cost": 0.003, "status": "SUCCESS"},
        {"modality": "text", "model_used": "gpt-4o", "latency_ms": 250, "tokens": 150, "cost": 0.005, "status": "SUCCESS"},
        {"modality": "text", "model_used": "gpt-4o", "latency_ms": 300, "tokens": 200, "cost": 0.006, "status": "SUCCESS"},
        {"modality": "code", "model_used": "claude-3-5-sonnet", "latency_ms": 500, "tokens": 300, "cost": 0.010, "status": "ERROR"},
    ]

    summary = AnalyticsEngine.process_events(sample_events)

    assert summary.total_events == 5
    assert summary.total_tokens == 750
    assert round(summary.total_cost, 3) == 0.026
    assert summary.success_rate == 80.0  # 4 out of 5

    # Check percentiles
    assert summary.latency_percentiles.min_ms == 120.0
    assert summary.latency_percentiles.max_ms == 500.0
    assert summary.latency_percentiles.p50_ms == 250.0

    # Check modality groups
    modalities = {m.modality: m for m in summary.modality_breakdown}
    assert "image" in modalities
    assert modalities["image"].count == 2
    assert modalities["image"].tokens == 100

    assert "text" in modalities
    assert modalities["text"].count == 2
    assert modalities["text"].tokens == 350

    # Check model efficiency
    models = {m.model_used: m for m in summary.model_efficiency}
    assert "midjourney-v6" in models
    assert models["midjourney-v6"].requests == 2

    # Check CSV export
    csv_out = AnalyticsEngine.to_csv_string(sample_events)
    assert "midjourney-v6" in csv_out
    assert "latency_ms" in csv_out


@pytest.mark.asyncio
async def test_api_analytics_endpoints():
    """Verify analytics telemetry tracking and reporting endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Log a few telemetry events
        for modality, model, lat in [("text", "gpt-4o", 150), ("image", "midjourney-v6", 210), ("code", "claude-3-5-sonnet", 320)]:
            t_res = await client.post(
                "/api/v1/analytics/events",
                json={
                    "event_name": "prompt.generate",
                    "modality": modality,
                    "model_used": model,
                    "latency_ms": lat,
                    "tokens": 120,
                    "cost": 0.003,
                    "status": "SUCCESS",
                },
            )
            assert t_res.status_code == 200

        # 2. Get analytics summary
        sum_res = await client.get("/api/v1/analytics/summary")
        assert sum_res.status_code == 200
        sum_data = sum_res.json()["data"]
        assert sum_data["total_events"] >= 3
        assert sum_data["total_tokens"] >= 360
        assert "latency_percentiles" in sum_data
        assert "cost_forecast" in sum_data

        # 3. Get modality breakdown
        mod_res = await client.get("/api/v1/analytics/modalities")
        assert mod_res.status_code == 200
        mod_items = mod_res.json()["data"]
        assert len(mod_items) >= 1

        # 4. Get latency percentiles
        lat_res = await client.get("/api/v1/analytics/latency")
        assert lat_res.status_code == 200
        lat_data = lat_res.json()["data"]
        assert lat_data["p50_ms"] > 0

        # 5. Get cost forecast
        fc_res = await client.get("/api/v1/analytics/forecast")
        assert fc_res.status_code == 200
        fc_data = fc_res.json()["data"]
        assert fc_data["projected_7_days"] >= 0

        # 6. Export telemetry CSV
        csv_res = await client.get("/api/v1/analytics/export")
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        assert "prompt.generate" in csv_res.text
