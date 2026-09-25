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
    # Root UI endpoint for NiceGUI (under mount_path '/ui')
    ui.page("/")(lambda: workspace_page("studio"))

    # Direct module deep-links
    ui.page("/studio")(lambda: workspace_page("studio"))
    ui.page("/optimizer")(lambda: workspace_page("optimizer"))
    ui.page("/evaluator")(lambda: workspace_page("evaluator"))
    ui.page("/agents")(lambda: workspace_page("agents"))
    ui.page("/rag")(lambda: workspace_page("rag"))
    ui.page("/library")(lambda: workspace_page("library"))
    ui.page("/analytics")(lambda: workspace_page("analytics"))
    ui.page("/security")(lambda: workspace_page("security"))
    ui.page("/versions")(lambda: workspace_page("versions"))
    ui.page("/admin")(lambda: workspace_page("admin"))


def mount_ui(app: FastAPI) -> None:
    """Mount NiceGUI on FastAPI application with custom title and styling."""
    register_ui_routes()
    ui.run_with(
        app,
        mount_path="/ui",
        title="PromptForge AI - Enterprise Prompt Engineering",
        dark=True,
    )
