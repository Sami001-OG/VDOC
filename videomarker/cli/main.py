"""VideoMarker CLI — command-line interface for video processing."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from videomarker.config.settings import VideoMarkerSettings, load_settings

app = typer.Typer(
    name="videomarker",
    help="Convert videos into structured MarkDirectory format",
    add_completion=False,
)
console = Console()

_logger = logging.getLogger("videomarker")


def _setup_logging(verbose: bool = False) -> None:
    """Configure structured logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )


def _get_output_path(input_path: Path, output: Optional[Path]) -> Path:
    """Determine the output path for processing."""
    if output:
        return output
    return input_path.parent / f"{input_path.stem}.markdir"


@app.callback()
def callback(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file (.env or .yaml)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Global options."""
    _setup_logging(verbose)
    if config:
        ctx.ensure_object(dict)
        ctx.obj["config_path"] = config


@app.command()
def process(
    input: Path = typer.Argument(
        ..., help="Input video file or directory of videos", exists=True
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory"
    ),
    summary: bool = typer.Option(False, "--summary", help="Generate summary only"),
    transcript: bool = typer.Option(False, "--transcript", help="Generate transcript only"),
    ocr: bool = typer.Option(False, "--ocr", help="Run OCR only"),
    chapters: bool = typer.Option(False, "--chapters", help="Detect chapters only"),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export format (markdown, json)"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
    resume: bool = typer.Option(False, "--resume", help="Resume interrupted processing"),
) -> None:
    """Process a video file and generate a MarkDirectory."""
    settings = load_settings(str(config) if config else None)

    if summary:
        settings.enabled_processors = ["semantic"]
    elif transcript:
        settings.enabled_processors = ["transcript"]
    elif ocr:
        settings.enabled_processors = ["ocr"]
    elif chapters:
        settings.enabled_processors = ["semantic"]

    if resume:
        settings.resume = True

    if export:
        settings.export_formats = [export]

    input_path = Path(input)

    if input_path.is_dir():
        # Batch process all videos in directory
        video_files = list(input_path.rglob("*"))
        video_files = [
            f for f in video_files
            if f.suffix.lower() in [".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v"]
        ]
        if not video_files:
            console.print("[red]No video files found in directory.[/red]")
            raise typer.Exit(1)

        console.print(f"[bold]Processing {len(video_files)} videos...[/bold]")
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Processing videos...", total=len(video_files))
            for vf in video_files:
                try:
                    out_dir = _get_output_path(vf, output)
                    process_single_video(vf, out_dir, settings)
                    results.append((vf, out_dir, "success"))
                except Exception as e:
                    _logger.error("Failed to process %s: %s", vf, e)
                    results.append((vf, None, str(e)))
                progress.update(task, advance=1)

        # Report results
        success = sum(1 for r in results if r[2] == "success")
        failed = len(results) - success
        console.print(f"\n[green]Processed: {success} videos[/green]")
        if failed:
            console.print(f"[red]Failed: {failed} videos[/red]")
            for vf, _, err in results:
                if err != "success":
                    console.print(f"  [red]{vf.name}: {err}[/red]")
    else:
        out_dir = _get_output_path(input_path, output)
        process_single_video(input_path, out_dir, settings)


def process_single_video(
    video_path: Path, output_dir: Path, settings: VideoMarkerSettings
) -> None:
    """Process a single video file."""
    from videomarker.core.pipeline import Pipeline
    from videomarker.core.plugin import PluginRegistry

    console.print(f"\n[bold blue]VideoMarker[/bold blue] — Processing: [yellow]{video_path}[/yellow]")

    # Initialize plugin system
    PluginRegistry.discover()
    plugins = PluginRegistry.get_all_plugins()
    if plugins:
        console.print(f"  Loaded {len(plugins)} processors: {', '.join(p.name for p in plugins)}")

    # Run pipeline
    pipeline = Pipeline(settings=settings)
    context = pipeline.run(video_path, output_dir=output_dir)

    # Report
    console.print(f"\n[green]✓[/green] Output: [bold]{output_dir}[/bold]")
    if context.errors:
        console.print(f"[yellow]Warnings: {len(context.errors)}[/yellow]")
    else:
        console.print(f"[green]All steps completed successfully.[/green]")


@app.command()
def list_processors() -> None:
    """List all available processor plugins."""
    from videomarker.core.plugin import PluginRegistry

    PluginRegistry.discover()
    plugins = PluginRegistry.get_all_plugins()

    if not plugins:
        console.print("[yellow]No processors found.[/yellow]")
        return

    console.print("[bold]Available Processors:[/bold]\n")
    for plugin in plugins:
        console.print(f"  [cyan]{plugin.name}[/cyan]")
        console.print(f"    Priority: {plugin.priority}")
        console.print(f"    Dependencies: {plugin.dependencies or 'none'}")
        console.print(f"    Class: {plugin.processor_class.__name__}")
        console.print()


@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8080,
    config: Optional[Path] = None,
) -> None:
    """Start the VideoMarker REST API server."""
    import uvicorn

    console.print(f"[bold blue]VideoMarker API[/bold blue] — Starting server on {host}:{port}")
    uvicorn.run(
        "videomarker.api.server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


@app.command()
def version() -> None:
    """Show the installed version."""
    from videomarker import __version__
    console.print(f"[bold]VideoMarker[/bold] v{__version__}")


if __name__ == "__main__":
    app()
