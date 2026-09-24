"""
PromptForge AI - UI Dashboard Page.
"""

from nicegui import ui
from app.ui.layout import page_layout


@page_layout("Dashboard - PromptForge AI")
async def dashboard_page():
    """Render the executive dashboard overview."""
    with ui.column().classes("w-full gap-6"):
        # Hero Banner
        with ui.card().classes("glass-panel w-full p-8 relative overflow-hidden"):
            with ui.column().classes("gap-2 z-10"):
                ui.label("Enterprise Prompt Engineering Platform").classes("text-3xl font-extrabold text-white")
                ui.label(
                    "Autonomous multi-agent synthesis, multi-dimensional heuristic evaluation, "
                    "RAG vector knowledge retrieval, and git-like version control for production AI workflows."
                ).classes("text-slate-300 text-sm max-w-2xl leading-relaxed")
                with ui.row().classes("gap-4 mt-4"):
                    ui.button("Open Prompt Studio", on_click=lambda: ui.navigate.to("/ui/studio")).classes("glow-btn px-6 py-2")
                    ui.button("Run Evaluator", on_click=lambda: ui.navigate.to("/ui/evaluator")).props("outline color=indigo").classes("px-6 py-2")

        # Metric Cards Grid
        with ui.grid(columns=4).classes("w-full gap-4"):
            with ui.card().classes("glass-panel p-5"):
                ui.label("Supported Modalities").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label("8 Modalities").classes("text-2xl font-bold text-indigo-400 mt-1")
                ui.label("Text, Image, Video, Code, Audio, Kids, Adult, Agent").classes("text-xs text-slate-500 mt-1")

            with ui.card().classes("glass-panel p-5"):
                ui.label("Prompt Evaluation Rubric").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label("7 Dimensions").classes("text-2xl font-bold text-emerald-400 mt-1")
                ui.label("Clarity, Specificity, Context, Constraints, etc.").classes("text-xs text-slate-500 mt-1")

            with ui.card().classes("glass-panel p-5"):
                ui.label("Multi-Agent Graph").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label("6 Agents").classes("text-2xl font-bold text-blue-400 mt-1")
                ui.label("Planner, Intent, Knowledge, Builder, Critic, Safety").classes("text-xs text-slate-500 mt-1")

            with ui.card().classes("glass-panel p-5"):
                ui.label("Model Router").classes("text-xs uppercase tracking-wider text-slate-400 font-semibold")
                ui.label("Multi-Provider").classes("text-2xl font-bold text-amber-400 mt-1")
                ui.label("Gemini, OpenAI, Anthropic, Ollama, Mock").classes("text-xs text-slate-500 mt-1")

        # Quick Navigation Cards
        ui.label("Quick Access Workspaces").classes("text-lg font-bold text-white mt-4")
        with ui.grid(columns=3).classes("w-full gap-4"):
            with ui.card().classes("glass-panel p-6 cursor-pointer hover:scale-[1.01] transition-transform").on(
                "click", lambda: ui.navigate.to("/ui/studio")
            ):
                with ui.row().classes("items-center gap-3 mb-2"):
                    ui.icon("auto_fix_high", color="indigo-400", size="1.8rem")
                    ui.label("Prompt Studio").classes("text-lg font-semibold text-white")
                ui.label("Generate modality-specific prompts with real-time parameter tuning and variable bindings.").classes(
                    "text-xs text-slate-400"
                )

            with ui.card().classes("glass-panel p-6 cursor-pointer hover:scale-[1.01] transition-transform").on(
                "click", lambda: ui.navigate.to("/ui/optimizer")
            ):
                with ui.row().classes("items-center gap-3 mb-2"):
                    ui.icon("tune", color="amber-400", size="1.8rem")
                    ui.label("Prompt Optimizer").classes("text-lg font-semibold text-white")
                ui.label("Transform vague, under-specified prompts into production-grade prompts with side-by-side diffs.").classes(
                    "text-xs text-slate-400"
                )

            with ui.card().classes("glass-panel p-6 cursor-pointer hover:scale-[1.01] transition-transform").on(
                "click", lambda: ui.navigate.to("/ui/library")
            ):
                with ui.row().classes("items-center gap-3 mb-2"):
                    ui.icon("menu_book", color="emerald-400", size="1.8rem")
                    ui.label("Library & Versions").classes("text-lg font-semibold text-white")
                ui.label("Git-like immutable version control, branch tags, line-by-line diffs, and format export.").classes(
                    "text-xs text-slate-400"
                )
