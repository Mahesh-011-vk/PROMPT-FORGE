"""
PromptForge AI - NiceGUI Master Application Assembly.

Mounts and registers all UI page routes onto the FastAPI application instance.
Provides a unified, single-link workspace experience across all platform capabilities.
"""

from fastapi import FastAPI
from nicegui import ui

from app.ui.pages.workspace import workspace_page


def register_ui_routes():
    """Register all interactive page endpoints pointing to the unified workspace."""
    # Root UI endpoints
    ui.page("/ui")(lambda: workspace_page("studio"))
    ui.page("/ui/")(lambda: workspace_page("studio"))

    # Direct module deep-links
    ui.page("/ui/studio")(lambda: workspace_page("studio"))
    ui.page("/ui/optimizer")(lambda: workspace_page("optimizer"))
    ui.page("/ui/evaluator")(lambda: workspace_page("evaluator"))
    ui.page("/ui/agents")(lambda: workspace_page("agents"))
    ui.page("/ui/rag")(lambda: workspace_page("rag"))
    ui.page("/ui/library")(lambda: workspace_page("library"))
    ui.page("/ui/analytics")(lambda: workspace_page("analytics"))
    ui.page("/ui/security")(lambda: workspace_page("security"))
    ui.page("/ui/admin")(lambda: workspace_page("admin"))


def mount_ui(app: FastAPI) -> None:
    """Mount NiceGUI on FastAPI application with custom title and styling."""
    register_ui_routes()
    ui.run_with(
        app,
        mount_path="/ui",
        title="PromptForge AI - Enterprise Prompt Engineering",
        dark=True,
    )
