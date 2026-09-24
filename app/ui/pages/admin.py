"""
PromptForge AI - Admin & System Settings Page.
"""

from nicegui import ui

from app.config.settings import settings
from app.ui.layout import page_layout


@page_layout("Settings & Providers - PromptForge AI")
async def admin_page():
    """System configuration, AI provider statuses, and security quotas."""
    with ui.column().classes("w-full gap-6"):
        with ui.column().classes("gap-1"):
            ui.label("Settings & System Architecture").classes("text-2xl font-bold text-white")
            ui.label("Inspect active LLM providers, database connection, and security thresholds.").classes("text-xs text-slate-400")

        # Provider Status Grid
        ui.label("Model Providers & Gateways").classes("text-sm font-bold text-indigo-300 uppercase tracking-wider mt-2")
        with ui.grid(columns=3).classes("w-full gap-4"):
            providers = [
                ("Mock Provider", "READY", "Default zero-latency deterministic mock engine", "emerald"),
                ("Google Gemini", "CONFIGURED" if settings.GEMINI_API_KEY else "DEMO FALLBACK", "Gemini 1.5 Pro & Flash multimodal models", "blue" if settings.GEMINI_API_KEY else "slate"),
                ("OpenAI", "CONFIGURED" if settings.OPENAI_API_KEY else "DEMO FALLBACK", "GPT-4o, GPT-4o-mini & embeddings", "blue" if settings.OPENAI_API_KEY else "slate"),
                ("Anthropic", "CONFIGURED" if settings.ANTHROPIC_API_KEY else "DEMO FALLBACK", "Claude 3.5 Sonnet & Haiku models", "blue" if settings.ANTHROPIC_API_KEY else "slate"),
                ("Ollama (Local)", "LOCAL HOST", f"Base URL: {settings.OLLAMA_BASE_URL}", "purple"),
                ("Circuit Breaker", "HEALTHY", "Automatic failover with exponential backoff", "emerald"),
            ]
            for name, status, desc, color in providers:
                with ui.card().classes("glass-panel p-5 gap-2"):
                    with ui.row().classes("justify-between items-center w-full"):
                        ui.label(name).classes("text-base font-bold text-white")
                        ui.badge(status, color=color).classes("text-xs font-mono")
                    ui.label(desc).classes("text-xs text-slate-400")

        # System Architecture & Storage
        ui.label("Storage & Security Thresholds").classes("text-sm font-bold text-emerald-300 uppercase tracking-wider mt-4")
        with ui.grid(columns=2).classes("w-full gap-4"):
            with ui.card().classes("glass-panel p-5 gap-3"):
                ui.label("Database & Cache").classes("text-sm font-semibold text-white")
                with ui.column().classes("gap-1 text-xs font-mono text-slate-300"):
                    ui.label(f"Database Type: {'SQLite (Async)' if settings.is_sqlite else 'PostgreSQL'}")
                    ui.label(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}")
                    ui.label(f"Vector Index: In-Memory Cosine Similarity ({settings.EMBEDDING_DIMENSION}-dim)")
                    ui.label(f"RAG Knowledge Base: {'ENABLED' if settings.ENABLE_RAG else 'DISABLED'}")

            with ui.card().classes("glass-panel p-5 gap-3"):
                ui.label("Rate Limit Quotas (Requests / Min)").classes("text-sm font-semibold text-white")
                with ui.column().classes("gap-1 text-xs font-mono text-slate-300"):
                    ui.label(f"Anonymous Tier: {settings.RATE_LIMITS.ANONYMOUS} req/min")
                    ui.label(f"User Tier: {settings.RATE_LIMITS.USER} req/min")
                    ui.label(f"Power User Tier: {settings.RATE_LIMITS.POWER_USER} req/min")
                    ui.label(f"Admin Tier: {settings.RATE_LIMITS.ADMIN} req/min")
                    ui.label(f"Injection Defense: {'ACTIVE' if settings.ENABLE_PROMPT_INJECTION_DEFENSE else 'INACTIVE'}")
