"""
PromptForge AI - Prompt Optimizer & Repair Page.
"""

from nicegui import ui

from app.config.constants import Modality
from app.schemas.optimizer import PromptOptimizeRequest
from app.services.optimizer_service import optimizer_service
from app.ui.layout import page_layout


@page_layout("Prompt Optimizer - PromptForge AI")
async def optimizer_page():
    """Interactive prompt optimization, ambiguity repair, and enhancement interface."""
    with ui.column().classes("w-full gap-6"):
        with ui.column().classes("gap-1"):
            ui.label("Prompt Optimizer & Repair").classes("text-2xl font-bold text-white")
            ui.label("Upgrade vague, under-specified prompts into high-performing, constraint-rich prompts.").classes("text-xs text-slate-400")

        # Top Controls Card
        with ui.card().classes("glass-panel w-full p-6 gap-4"):
            ui.label("Input Under-Specified Prompt").classes("text-sm font-bold text-indigo-300 uppercase tracking-wider")

            input_prompt = ui.textarea(
                label="Raw Draft Prompt",
                placeholder="e.g., A picture of a car in a city...",
                value="A picture of a luxury sports car at night in a city.",
            ).classes("w-full font-mono").props("rows=3 outlined")

            with ui.row().classes("w-full gap-4 items-center"):
                modality_sel = ui.select(
                    label="Target Modality",
                    options=["text", "image", "video", "code"],
                    value="image",
                ).classes("w-48").props("outlined")

                opt_btn = ui.button("Optimize & Repair Prompt", icon="auto_fix_high").classes("glow-btn px-6 py-2")
                delta_badge = ui.badge("Improvement Delta: --", color="amber").classes("text-sm font-mono px-3 py-1")

        # Side by Side Comparison
        with ui.row().classes("w-full gap-6 items-start"):
            # Original Card
            with ui.card().classes("glass-panel flex-1 p-6 gap-3"):
                ui.label("Original Draft").classes("text-sm font-bold text-slate-400 uppercase tracking-wider")
                orig_display = ui.textarea().classes("w-full font-mono text-slate-300").props("rows=6 outlined readonly")
                orig_score_label = ui.label("Initial Score: --").classes("text-xs text-slate-400 font-mono")

            # Optimized Card
            with ui.card().classes("glass-panel flex-1 p-6 gap-3"):
                ui.label("Optimized Production Prompt").classes("text-sm font-bold text-emerald-300 uppercase tracking-wider")
                opt_display = ui.textarea().classes("w-full font-mono text-emerald-200").props("rows=6 outlined readonly")
                opt_score_label = ui.label("Optimized Score: --").classes("text-xs text-emerald-400 font-mono")

        # Improvements Checklist
        with ui.card().classes("glass-panel w-full p-6 gap-2"):
            ui.label("Applied Heuristic & Structural Enhancements").classes("text-sm font-bold text-indigo-300 uppercase tracking-wider")
            improvements_container = ui.column().classes("gap-1 text-xs text-slate-300")
            ui.label("Click 'Optimize & Repair' to run the enhancement pipeline.").classes("text-xs text-slate-500")

        # Handler
        async def on_optimize():
            if not input_prompt.value or not input_prompt.value.strip():
                ui.notify("Please enter a prompt to optimize.", type="warning")
                return

            mod_enum = None
            try:
                mod_enum = Modality(modality_sel.value)
            except Exception:
                mod_enum = Modality.TEXT

            req = PromptOptimizeRequest(
                prompt=input_prompt.value.strip(),
                modality=mod_enum,
            )
            res = await optimizer_service.optimize(req)

            orig_display.value = res.original_prompt
            opt_display.value = res.optimized_prompt
            orig_score_label.text = f"Initial Score: {res.score_before}/100"
            opt_score_label.text = f"Optimized Score: {res.score_after}/100"
            delta = round(res.score_after - res.score_before, 1)
            delta_badge.text = f"Improvement: +{delta} pts"

            improvements_container.clear()
            with improvements_container:
                for imp in res.why_improved:
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle", color="emerald-400", size="1rem")
                        ui.label(imp)

            ui.notify(f"Optimization complete! Score boosted by +{delta}", type="positive")

        opt_btn.on("click", on_optimize)
