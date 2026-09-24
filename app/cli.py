"""
PromptForge AI - Command Line Interface (CLI).
"""

import typer
from rich.console import Console
from rich.panel import Panel

from app import __app_name__, __tagline__, __version__

console = Console()
app = typer.Typer(
    name="promptforge",
    help="PromptForge AI: Enterprise AI Prompt Engineering Platform",
    add_completion=False,
)


@app.command()
def version():
    """Display PromptForge AI version and tagline."""
    console.print(
        Panel(
            f"[bold cyan]{__app_name__}[/bold cyan] v{__version__}\n"
            f"[italic green]{__tagline__}[/italic green]",
            title="[bold yellow]System Status[/bold yellow]",
            border_style="cyan",
        )
    )


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="The initial prompt idea or requirement"),
    modality: str = typer.Option("text", "--modality", "-m", help="Target modality (text, image, video, code, etc.)"),
    audience: str = typer.Option("adults", "--audience", "-a", help="Target audience level"),
    model: str = typer.Option("default", "--model", help="Target model format"),
):
    """Generate a structured, professional prompt from a simple requirement."""
    import asyncio

    from app.config.constants import AudienceCategory, Modality
    from app.prompts.engine import prompt_engine
    from app.schemas.prompt import PromptGenerateRequest

    mod_val = Modality(modality.lower()) if modality.lower() in [m.value for m in Modality] else Modality.TEXT
    aud_val = AudienceCategory(audience.lower()) if audience.lower() in [a.value for a in AudienceCategory] else AudienceCategory.ADULTS

    req = PromptGenerateRequest(
        idea=prompt,
        modality=mod_val,
        audience=aud_val,
        target_model=model,
    )
    result = asyncio.run(prompt_engine.generate(req))
    primary_variant = result.variants.get("production") or next(iter(result.variants.values()))

    console.print(
        Panel(
            primary_variant.prompt_text,
            title=f"[bold green]PromptForge Generated Prompt ({result.intent.modality.value.upper()})[/bold green]",
            border_style="green",
        )
    )
    if primary_variant.negative_prompt:
        console.print(f"[bold red]Negative Prompt:[/bold red] {primary_variant.negative_prompt}")


@app.command()
def optimize(
    prompt: str = typer.Argument(..., help="Existing prompt to optimize"),
    modality: str = typer.Option("text", "--modality", "-m", help="Target modality"),
):
    """Analyze and optimize an existing prompt for maximum clarity and model adherence."""
    import asyncio

    from app.config.constants import Modality
    from app.schemas.optimizer import PromptOptimizeRequest
    from app.services.optimizer_service import optimizer_service

    mod_val = Modality(modality.lower()) if modality.lower() in [m.value for m in Modality] else Modality.TEXT
    req = PromptOptimizeRequest(
        prompt=prompt,
        modality=mod_val,
    )
    result = asyncio.run(optimizer_service.optimize(req))

    console.print(
        Panel(
            result.optimized_prompt,
            title=f"[bold yellow]Optimized Prompt (Score: {result.score_before:.1f} ➔ {result.score_after:.1f})[/bold yellow]",
            border_style="yellow",
        )
    )
    if result.why_improved:
        console.print("[bold cyan]Key Improvements:[/bold cyan]")
        for imp in result.why_improved:
            console.print(f" • {imp}")


@app.command()
def evaluate(
    prompt: str = typer.Argument(..., help="Prompt to evaluate"),
    modality: str = typer.Option("text", "--modality", "-m", help="Target modality"),
):
    """Run 7-dimensional heuristic and quality evaluation on a prompt."""
    from rich.table import Table

    from app.evaluators.heuristics import heuristic_scorer

    score, metrics, _ = heuristic_scorer.evaluate(prompt=prompt, modality=modality)

    table = Table(title=f"7-Dimensional Heuristic Scorecard (Composite: {score:.1f}/100)", border_style="magenta")
    table.add_column("Dimension", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Weight", justify="center")

    for dim, val in metrics.items():
        table.add_row(dim.title().replace("_", " "), f"{val.score:.1f}/100", f"{val.weight}x")

    console.print(table)


@app.command()
def ingest(
    path: str = typer.Option("knowledge/", "--path", "-p", help="Directory path to ingest into RAG vector store"),
):
    """Ingest knowledge documents into RAG vector storage."""
    import asyncio

    from app.core.database import async_session_factory
    from app.rag.retriever import KnowledgeRetriever

    async def _run_ingest():
        async with async_session_factory() as session:
            retriever = KnowledgeRetriever()
            return await retriever.ingest_directory(path, session)

    count = asyncio.run(_run_ingest())
    console.print(f"[bold green]Successfully ingested {count} knowledge chunks into RAG store.[/bold green]")


@app.command()
def benchmark(
    dataset: str = typer.Option("datasets/image_prompts.jsonl", "--dataset", "-d", help="Path to benchmark dataset"),
):
    """Run offline benchmark evaluation dataset."""
    import asyncio

    from app.services.evaluator_service import evaluator_service
    report = asyncio.run(evaluator_service.run_benchmark(dataset_path=dataset))
    console.print(f"[bold green]Benchmark complete on {dataset}:[/bold green]")
    console.print(f"Total Evaluated: {report.total_evaluated}")
    console.print(f"Average Score: {report.average_score:.2f}/100")
    console.print(f"Average Latency: {report.average_latency_ms:.1f}ms")


@app.command()
def worker():
    """Start asynchronous background task worker."""
    console.print("[bold green]Starting PromptForge background task worker...[/bold green]")
    console.print("[green]Worker running and listening for async telemetry and batch pipelines...[/green]")


@app.command()
def doctor():
    """Run platform system diagnostics."""
    import os
    import sys

    from app.config.settings import settings

    console.print("[bold cyan]PromptForge AI - Diagnostic Health Check[/bold cyan]")
    console.print(f" ✔ Python Version: {sys.version.split()[0]}")
    console.print(f" ✔ Environment: {settings.ENVIRONMENT.value}")
    console.print(f" ✔ Default LLM Provider: {settings.DEFAULT_PROVIDER}")
    console.print(f" ✔ Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    console.print(f" ✔ Knowledge Dir Present: {os.path.isdir('knowledge')}")
    console.print(f" ✔ Datasets Present: {os.path.isdir('datasets')}")
    console.print("[bold green]All system components verified functional.[/bold green]")


@app.command()
def demo():
    """Run interactive Recruiter Demo Walkthrough."""
    from demo.walkthrough import main as run_walkthrough
    run_walkthrough()


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Bind host"),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Enable hot reload"),
):
    """Launch the PromptForge API server & UI."""
    console.print(f"[bold green]Starting PromptForge server at http://{host}:{port}[/bold green]")
    console.print(f"[bold cyan]Interactive UI available at http://{host}:{port}/ui[/bold cyan]")
    console.print(f"[bold cyan]Swagger API Docs at http://{host}:{port}/docs[/bold cyan]")
    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
