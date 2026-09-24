"""
PromptForge AI - Evaluation Lab Page.
"""

from nicegui import ui

from app.evaluators.heuristics import heuristic_scorer
from app.ui.layout import page_layout


@page_layout("Evaluation Lab - PromptForge AI")
async def evaluator_page():
    """Interactive prompt evaluation lab with multi-dimensional scorecards."""
    with ui.column().classes("w-full gap-6"):
        with ui.column().classes("gap-1"):
            ui.label("Evaluation Lab").classes("text-2xl font-bold text-white")
            ui.label("Benchmark prompts across 7 enterprise dimensions using transparent heuristic scoring.").classes("text-xs text-slate-400")

        # Input Card
        with ui.card().classes("glass-panel w-full p-6 gap-4"):
            prompt_input = ui.textarea(
                label="Prompt to Evaluate",
                placeholder="Enter prompt text here...",
                value="You are an expert Python backend engineer. Write an asynchronous rate limiter using token bucket algorithm with typing and tests.",
            ).classes("w-full font-mono").props("rows=3 outlined")

            with ui.row().classes("w-full gap-4 items-center"):
                eval_modality = ui.select(
                    label="Modality",
                    options=["text", "image", "video", "code"],
                    value="code",
                ).classes("w-48").props("outlined")

                eval_btn = ui.button("Evaluate Prompt", icon="analytics").classes("glow-btn px-6 py-2")
                overall_score_badge = ui.badge("Overall Score: --", color="emerald").classes("text-sm font-mono px-3 py-1")

        # Results Grid: 7 Dimensions + Feedback
        with ui.row().classes("w-full gap-6 items-start"):
            # Left: Dimensional Metrics Breakdown
            with ui.card().classes("glass-panel flex-1 p-6 gap-4"):
                ui.label("Dimensional Breakdown").classes("text-sm font-bold text-indigo-300 uppercase tracking-wider")
                metrics_container = ui.column().classes("w-full gap-3")
                ui.label("Run evaluation to inspect dimensional score breakdown.").classes("text-xs text-slate-500")

            # Right: Actionable Feedback & Critiques
            with ui.card().classes("glass-panel flex-1 p-6 gap-4"):
                ui.label("Actionable Feedback & Critiques").classes("text-sm font-bold text-amber-300 uppercase tracking-wider")
                feedback_container = ui.column().classes("w-full gap-2 text-xs text-slate-300")
                ui.label("Recommendations will appear after running evaluation.").classes("text-xs text-slate-500")

        async def on_eval():
            if not prompt_input.value or not prompt_input.value.strip():
                ui.notify("Please enter prompt text to evaluate.", type="warning")
                return

            score, metrics, feedback = heuristic_scorer.evaluate(
                prompt=prompt_input.value.strip(),
                modality=eval_modality.value,
            )
            overall_score_badge.text = f"Overall Score: {score}/100"

            # Render Metrics Breakdown
            metrics_container.clear()
            with metrics_container:
                for key, m in metrics.items():
                    with ui.column().classes("w-full gap-1"):
                        with ui.row().classes("justify-between w-full text-xs font-mono"):
                            ui.label(m.name).classes("font-semibold text-slate-200")
                            ui.label(f"{m.score}/100").classes("text-indigo-400 font-bold")
                        ui.linear_progress(value=m.score / 100.0, color="indigo").classes("rounded h-2")
                        ui.label(m.rationale).classes("text-[10px] text-slate-400 italic")

            # Render Feedback
            feedback_container.clear()
            with feedback_container:
                if not feedback:
                    with ui.row().classes("items-center gap-2 text-emerald-400"):
                        ui.icon("verified", size="1.2rem")
                        ui.label("No critical issues found! Prompt aligns with high-rigor standards.")
                else:
                    for fb in feedback:
                        with ui.row().classes("items-start gap-2"):
                            ui.icon("lightbulb", color="amber-400", size="1rem")
                            ui.label(fb).classes("text-slate-300 leading-tight")

            ui.notify(f"Evaluation finished with score {score}/100", type="positive")

        eval_btn.on("click", on_eval)
