"""
PromptForge AI - Prompt Generation Studio Page.
"""

import time

from nicegui import ui

from app.agents.orchestrator import AgentOrchestrator
from app.config.constants import Modality
from app.prompts.engine import prompt_engine
from app.schemas.agents import AgentOrchestrateRequest
from app.schemas.prompt import PromptGenerateRequest
from app.ui.layout import page_layout


@page_layout("Prompt Studio - PromptForge AI")
async def studio_page():
    """Interactive prompt generation and multi-agent synthesis studio."""
    with ui.column().classes("w-full gap-6"):
        with ui.row().classes("justify-between items-center w-full"):
            with ui.column().classes("gap-1"):
                ui.label("Prompt Studio").classes("text-2xl font-bold text-white")
                ui.label("Craft, parameterize, and compile production prompts across all modalities.").classes("text-xs text-slate-400")

        with ui.row().classes("w-full gap-6 items-start"):
            # Left Column: Configuration & Controls
            with ui.card().classes("glass-panel flex-1 p-6 gap-4"):
                ui.label("1. Configuration & Input").classes("text-sm font-bold text-indigo-300 uppercase tracking-wider")

                raw_input = ui.textarea(
                    label="Prompt Objective / Raw Input",
                    placeholder="e.g., A cinematic portrait of a cyberpunk cyber-doctor in neo Tokyo rain...",
                ).classes("w-full font-mono").props("rows=4 outlined")

                with ui.row().classes("w-full gap-4"):
                    modality_select = ui.select(
                        label="Modality",
                        options=["text", "image", "video", "code"],
                        value="image",
                    ).classes("flex-1").props("outlined")

                    model_select = ui.select(
                        label="Target Model",
                        options=["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro", "midjourney", "runway"],
                        value="midjourney",
                    ).classes("flex-1").props("outlined")

                with ui.row().classes("w-full gap-4"):
                    audience_select = ui.select(
                        label="Audience",
                        options=["general", "kids", "adults", "developers"],
                        value="general",
                    ).classes("flex-1").props("outlined")

                    persona_input = ui.input(
                        label="Persona / Role (Optional)",
                        placeholder="e.g., Senior Concept Artist",
                    ).classes("flex-1").props("outlined")

                # Action Buttons
                with ui.row().classes("w-full gap-4 mt-2"):
                    compile_btn = ui.button("Compile with Engine", icon="bolt").classes("glow-btn flex-1 py-2")
                    agent_btn = ui.button("Orchestrate Multi-Agent", icon="psychology").props("color=purple outline").classes("flex-1 py-2")

            # Right Column: Generated Output & Metrics
            with ui.card().classes("glass-panel flex-1 p-6 gap-4"):
                ui.label("2. Generated Artifact & Quality Score").classes("text-sm font-bold text-emerald-300 uppercase tracking-wider")

                with ui.row().classes("justify-between items-center w-full"):
                    score_badge = ui.badge("Score: --", color="emerald").classes("text-sm font-mono px-3 py-1")
                    status_label = ui.label("Awaiting generation...").classes("text-xs text-slate-400 font-mono")

                output_text = ui.textarea(
                    label="Generated Prompt Specification",
                    placeholder="Compiled prompt will appear here...",
                ).classes("w-full font-mono").props("rows=8 outlined readonly")

                neg_output = ui.textarea(
                    label="Negative Prompt (if applicable)",
                    placeholder="Negative constraints...",
                ).classes("w-full font-mono").props("rows=2 outlined readonly")

                with ui.row().classes("w-full justify-between items-center mt-2"):
                    copy_btn = ui.button("Copy Prompt", icon="content_copy").props("outline color=slate")
                    async def copy_prompt():
                        if output_text.value:
                            ui.run_javascript(f"navigator.clipboard.writeText({output_text.value!r})")
                            ui.notify("Prompt copied to clipboard!", type="positive")
                    copy_btn.on("click", copy_prompt)

        # Handlers
        async def on_compile_click():
            if not raw_input.value or not raw_input.value.strip():
                ui.notify("Please enter a prompt objective first.", type="warning")
                return

            status_label.text = "Compiling with Domain Engine..."
            start_t = time.perf_counter()

            mod_enum = None
            try:
                mod_enum = Modality(modality_select.value)
            except Exception:
                mod_enum = Modality.TEXT

            req = PromptGenerateRequest(
                idea=raw_input.value.strip(),
                modality=mod_enum,
                target_model=model_select.value,
            )
            res = await prompt_engine.generate(req)

            var = (
                res.variants.get("model_specific")
                or res.variants.get("expert")
                or next(iter(res.variants.values()))
            )
            output_text.value = var.prompt_text
            neg_output.value = var.negative_prompt or "None"
            score_badge.text = f"Score: {res.quality_score}/100"
            latency = int((time.perf_counter() - start_t) * 1000)
            status_label.text = f"Compiled in {latency}ms"
            ui.notify("Prompt successfully synthesized!", type="positive")

        async def on_agent_click():
            if not raw_input.value or not raw_input.value.strip():
                ui.notify("Please enter a prompt objective first.", type="warning")
                return

            status_label.text = "Running 6-Agent Pipeline..."
            req = AgentOrchestrateRequest(
                goal=raw_input.value.strip(),
                modality=modality_select.value,
                persona=persona_input.value or None,
                audience=audience_select.value,
                target_model=model_select.value,
            )
            res = await AgentOrchestrator.orchestrate(req)

            output_text.value = res.final_prompt
            neg_output.value = res.negative_prompt or "None"
            score_badge.text = f"Score: {res.quality_score}/10"
            status_label.text = f"6 Agents finished in {res.total_latency_ms}ms"
            ui.notify(f"Autonomous orchestration completed ({res.safety_verdict})!", type="positive")

        compile_btn.on("click", on_compile_click)
        agent_btn.on("click", on_agent_click)
