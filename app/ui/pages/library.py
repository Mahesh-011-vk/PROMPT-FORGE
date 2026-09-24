"""
PromptForge AI - Prompt Library & Version Control Page.
"""

from nicegui import ui

from app.core.database import async_session_factory
from app.services.library_service import LibraryService
from app.ui.layout import page_layout


@page_layout("Prompt Library - PromptForge AI")
async def library_page():
    """Prompt library catalog, search, and git-like version control browser."""
    with ui.column().classes("w-full gap-6"):
        with ui.row().classes("justify-between items-center w-full"):
            with ui.column().classes("gap-1"):
                ui.label("Prompt Library & Version Control").classes("text-2xl font-bold text-white")
                ui.label("Search repository prompts, inspect commit history, and export in multiple formats.").classes("text-xs text-slate-400")

        # Search & Filter Controls
        with ui.card().classes("glass-panel w-full p-4 gap-4"):
            with ui.row().classes("w-full gap-4 items-center"):
                search_input = ui.input(
                    placeholder="Search by title, keywords, or tags...",
                ).classes("flex-1").props("outlined dense clearable")

                modality_filter = ui.select(
                    options=["all", "text", "image", "video", "code"],
                    value="all",
                    label="Modality",
                ).classes("w-36").props("outlined dense")

                refresh_btn = ui.button("Search / Refresh", icon="search").classes("glow-btn px-4")

        # Prompts List Container
        prompts_container = ui.column().classes("w-full gap-4")

        async def load_prompts():
            prompts_container.clear()
            mod = None if modality_filter.value == "all" else modality_filter.value
            query = search_input.value.strip() if search_input.value else None

            async with async_session_factory() as session:
                prompts, total = await LibraryService.list_prompts(
                    db=session,
                    query=query,
                    modality=mod,
                    limit=20,
                )

            with prompts_container:
                if not prompts:
                    with ui.card().classes("glass-panel w-full p-8 text-center"):
                        ui.label("No prompts found matching current criteria.").classes("text-slate-400 text-sm")
                        ui.label("Create prompts in Prompt Studio to populate the repository.").classes("text-slate-500 text-xs mt-1")
                    return

                for p in prompts:
                    with ui.card().classes("glass-panel w-full p-5 gap-3"):
                        with ui.row().classes("justify-between items-center w-full"):
                            with ui.row().classes("items-center gap-3"):
                                ui.label(p["title"]).classes("text-base font-bold text-white")
                                ui.badge(p["modality"].upper(), color="indigo").classes("text-xs font-mono")
                                if p.get("quality_score"):
                                    ui.badge(f"Score: {p['quality_score']}", color="emerald").classes("text-xs font-mono")
                            with ui.row().classes("items-center gap-2"):
                                ui.badge(f"v{p.get('version_count', 1)}", color="purple").classes("text-xs font-mono")

                        # Prompt Text Preview
                        with ui.card().classes("glass-card w-full p-3 font-mono text-xs text-slate-300"):
                            ui.label(p.get("current_prompt_text", p.get("raw_input", "")))

                        # Tags Row
                        if p.get("tags"):
                            with ui.row().classes("gap-2 mt-1"):
                                for t in p["tags"]:
                                    ui.badge(f"#{t}", color="slate").classes("text-[10px]")

        refresh_btn.on("click", load_prompts)
        await load_prompts()
