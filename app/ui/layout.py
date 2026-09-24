"""
PromptForge AI - Base Layout Component for NiceGUI.
"""

from collections.abc import Callable

from nicegui import ui

from app.ui.styles import GLASS_CSS


def page_layout(title: str = "PromptForge AI"):
    """Decorator or wrapper that renders common navigation header and dark container."""

    def decorator(fn: Callable):
        async def wrapper(*args, **kwargs):
            ui.add_head_html(GLASS_CSS)
            ui.dark_mode().enable()

            # Global Navigation Header
            with ui.header().classes("glass-panel justify-between items-center px-8 py-3 mb-6 sticky top-0 z-50"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("bolt", size="2rem", color="indigo-400")
                    with ui.column().classes("gap-0"):
                        ui.label("PROMPTFORGE AI").classes("text-xl font-bold tracking-wider text-white")
                        ui.label("Generate. Optimize. Test. Evaluate. Deploy.").classes("text-xs text-indigo-300 font-mono")

                with ui.row().classes("items-center gap-6"):
                    ui.link("Dashboard", "/ui/").classes("nav-link text-sm")
                    ui.link("Prompt Studio", "/ui/studio").classes("nav-link text-sm")
                    ui.link("Optimizer", "/ui/optimizer").classes("nav-link text-sm")
                    ui.link("Evaluation Lab", "/ui/evaluator").classes("nav-link text-sm")
                    ui.link("Library", "/ui/library").classes("nav-link text-sm")
                    ui.link("Analytics", "/ui/analytics").classes("nav-link text-sm")
                    ui.link("Settings", "/ui/admin").classes("nav-link text-sm")

                with ui.row().classes("items-center gap-2"):
                    ui.badge("v0.1.0-PROD", color="indigo").classes("text-xs font-mono")

            # Main Content Area
            with ui.column().classes("w-full max-w-7xl mx-auto px-6 pb-12 gap-6"):
                await fn(*args, **kwargs)

        return wrapper

    return decorator
