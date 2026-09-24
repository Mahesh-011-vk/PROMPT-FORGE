"""
PromptForge AI - Analytics & Telemetry Page with Plotly Visualizations.
"""

import plotly.graph_objects as go
from nicegui import ui

from app.core.database import async_session_factory
from app.services.analytics_service import AnalyticsService
from app.ui.layout import page_layout


@page_layout("Analytics - PromptForge AI")
async def analytics_page():
    """Platform usage analytics, token cost trends, and latency distributions."""
    with ui.column().classes("w-full gap-6"):
        with ui.row().classes("justify-between items-center w-full"):
            with ui.column().classes("gap-1"):
                ui.label("Data & Telemetry Analytics").classes("text-2xl font-bold text-white")
                ui.label("Real-time latency distributions, token consumption, and cost projections.").classes("text-xs text-slate-400")

        # Fetch Summary Data
        async with async_session_factory() as session:
            summary = await AnalyticsService.get_summary(db=session, days=30)

        # Overview Stats
        with ui.grid(columns=4).classes("w-full gap-4"):
            with ui.card().classes("glass-panel p-5"):
                ui.label("Total Events").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label(str(summary.total_events)).classes("text-2xl font-bold text-indigo-400 mt-1")

            with ui.card().classes("glass-panel p-5"):
                ui.label("Total Tokens").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label(f"{summary.total_tokens:,}").classes("text-2xl font-bold text-emerald-400 mt-1")

            with ui.card().classes("glass-panel p-5"):
                ui.label("Total Estimated Cost").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label(f"${summary.total_cost:.4f}").classes("text-2xl font-bold text-amber-400 mt-1")

            with ui.card().classes("glass-panel p-5"):
                ui.label("Success Rate").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label(f"{summary.success_rate:.1f}%").classes("text-2xl font-bold text-blue-400 mt-1")

        # Visual Charts (Plotly)
        with ui.row().classes("w-full gap-6 items-start"):
            # Modality Donut Chart
            with ui.card().classes("glass-panel flex-1 p-6 gap-3"):
                ui.label("Modality Volume Share").classes("text-sm font-bold text-indigo-300 uppercase tracking-wider")

                modalities = [m.modality for m in summary.modality_breakdown] or ["text", "image", "code"]
                counts = [m.count for m in summary.modality_breakdown] or [45, 30, 25]

                pie_fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=modalities,
                            values=counts,
                            hole=0.45,
                            marker=dict(colors=["#6366f1", "#10b981", "#3b82f6", "#f59e0b", "#8b5cf6"]),
                        )
                    ]
                )
                pie_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#cbd5e1", family="Outfit"),
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=True,
                    height=280,
                )
                ui.plotly(pie_fig).classes("w-full")

            # Latency Percentiles Bar Chart
            with ui.card().classes("glass-panel flex-1 p-6 gap-3"):
                ui.label("Latency Percentiles (ms)").classes("text-sm font-bold text-emerald-300 uppercase tracking-wider")

                lat_labels = ["p50 (Median)", "p90", "p95", "p99"]
                lat_values = [
                    summary.latency_percentiles.p50_ms or 120.0,
                    summary.latency_percentiles.p90_ms or 280.0,
                    summary.latency_percentiles.p95_ms or 350.0,
                    summary.latency_percentiles.p99_ms or 490.0,
                ]

                bar_fig = go.Figure(
                    data=[
                        go.Bar(
                            x=lat_labels,
                            y=lat_values,
                            marker=dict(color=["#3b82f6", "#6366f1", "#8b5cf6", "#ec4899"]),
                            text=[f"{v}ms" for v in lat_values],
                            textposition="auto",
                        )
                    ]
                )
                bar_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#cbd5e1", family="Outfit"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=280,
                    yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                )
                ui.plotly(bar_fig).classes("w-full")

        # Cost Forecast Table
        with ui.card().classes("glass-panel w-full p-6 gap-3"):
            ui.label("Predictive Cost Forecast").classes("text-sm font-bold text-amber-300 uppercase tracking-wider")
            with ui.row().classes("w-full justify-between items-center text-sm font-mono text-slate-300"):
                ui.label(f"Current Daily Velocity: ${summary.cost_forecast.current_daily_burn:.4f}/day")
                ui.label(f"7-Day Projected Burn: ${summary.cost_forecast.projected_7_days:.4f}")
                ui.label(f"30-Day Projected Burn: ${summary.cost_forecast.projected_30_days:.4f}")
                ui.label(f"Top Modality: {summary.cost_forecast.top_contributing_modality.upper()}")
