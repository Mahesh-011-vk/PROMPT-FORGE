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
    audience: str = typer.Option("general", "--audience", "-a", help="Target audience level"),
    model: str = typer.Option("default", "--model", help="Target model format"),
):
    """Generate a structured, professional prompt from a simple requirement."""
    console.print(f"[bold cyan]Input idea:[/bold cyan] {prompt}")
    console.print(f"[cyan]Modality:[/cyan] {modality} | [cyan]Audience:[/cyan] {audience} | [cyan]Target Model:[/cyan] {model}")
    console.print("[dim yellow]Generation engine will be invoked in Phase 5.[/dim yellow]")


@app.command()
def optimize(
    prompt: str = typer.Argument(..., help="Existing prompt to optimize"),
):
    """Analyze and optimize an existing prompt for maximum clarity and model adherence."""
    console.print(f"[bold cyan]Optimizing prompt:[/bold cyan] {prompt}")
    console.print("[dim yellow]Optimizer engine will be invoked in Phase 8.[/dim yellow]")


@app.command()
def evaluate(
    prompt: str = typer.Argument(..., help="Prompt to evaluate"),
):
    """Run AI-as-a-judge heuristic and quality evaluation on a prompt."""
    console.print(f"[bold cyan]Evaluating prompt:[/bold cyan] {prompt}")
    console.print("[dim yellow]Evaluation engine will be invoked in Phase 9.[/dim yellow]")


@app.command()
def ingest(
    path: str = typer.Option("knowledge/", "--path", "-p", help="Directory path to ingest into RAG vector store"),
):
    """Ingest knowledge documents into RAG vector storage."""
    console.print(f"[bold cyan]Ingesting documents from:[/bold cyan] {path}")
    console.print("[dim yellow]RAG pipeline will be invoked in Phase 10.[/dim yellow]")


@app.command()
def benchmark(
    dataset: str = typer.Option("datasets/image_prompts.jsonl", "--dataset", "-d", help="Path to benchmark dataset"),
):
    """Run offline benchmark evaluation dataset."""
    console.print(f"[bold cyan]Running benchmark dataset:[/bold cyan] {dataset}")
    console.print("[dim yellow]Benchmark suite will be invoked in Phase 9/19.[/dim yellow]")


@app.command()
def worker():
    """Start asynchronous background task worker."""
    console.print("[bold green]Starting PromptForge background task worker...[/bold green]")
    console.print("[dim yellow]Worker queue will be started in Phase 14.[/dim yellow]")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Bind host"),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port"),
    reload: bool = typer.Option(True, "--reload", help="Enable hot reload"),
):
    """Launch the PromptForge API server."""
    console.print(f"[bold green]Starting PromptForge server at http://{host}:{port}[/bold green]")
    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
