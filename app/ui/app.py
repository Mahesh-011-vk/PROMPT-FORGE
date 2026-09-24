"""
PromptForge AI - NiceGUI Master Application Assembly.

Mounts and registers all UI page routes onto the FastAPI application instance.
"""

from fastapi import FastAPI
from nicegui import ui

from app.ui.pages.admin import admin_page
from app.ui.pages.analytics import analytics_page
from app.ui.pages.dashboard import dashboard_page
from app.ui.pages.evaluator import evaluator_page
from app.ui.pages.library import library_page
from app.ui.pages.optimizer import optimizer_page
from app.ui.pages.studio import studio_page


def register_ui_routes():
    """Register all interactive page endpoints."""
    ui.page("/ui")(dashboard_page)
    ui.page("/ui/")(dashboard_page)
    ui.page("/ui/studio")(studio_page)
    ui.page("/ui/optimizer")(optimizer_page)
    ui.page("/ui/evaluator")(evaluator_page)
    ui.page("/ui/library")(library_page)
    ui.page("/ui/analytics")(analytics_page)
    ui.page("/ui/admin")(admin_page)


def mount_ui(app: FastAPI) -> None:
    """Mount NiceGUI on FastAPI application with custom title and styling."""
    register_ui_routes()
    ui.run_with(
        app,
        mount_path="/ui",
        title="PromptForge AI - Enterprise Prompt Engineering",
        dark=True,
    )
