"""VDOC CLI — thin presentation layer. All business logic in vdoc.services."""

from __future__ import annotations

import json
import logging
import shutil
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from vdoc.config.manager import ConfigManager
from vdoc.services import PipelineService, ProviderService

app = typer.Typer(name="vdoc", help="Video → Document. Structured. Searchable. Semantic.")
console = Console()
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])


@app.callback()
def callback(ctx: typer.Context) -> None:
    ctx.ensure_object(dict)


@app.command()
def process(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file (YAML)"),
    resume: bool = typer.Option(False, "--resume", help="Resume from last checkpoint"),
    no_transcript: bool = typer.Option(False, "--no-transcript", help="Skip transcription"),
    no_ocr: bool = typer.Option(False, "--no-ocr", help="Skip OCR"),
    no_vision: bool = typer.Option(False, "--no-vision", help="Skip vision analysis"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Skip LLM analysis"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing output"),
) -> None:
    """Process a video into a structured MarkDirectory."""
    cfg = PipelineService.load_config(
        video, output, config,
        overwrite=overwrite,
        speech_provider="none" if no_transcript else None,
        ocr_provider="none" if no_ocr else None,
        vision_provider="none" if no_vision else None,
        llm_provider="none" if no_llm else None,
    )
    console.print(f"[bold cyan]VDOC[/bold cyan] Processing: [white]{video.name}[/white]")

    pipeline = PipelineService.build_pipeline(cfg)
    ctx = PipelineService.create_context(str(video), cfg["output_dir"], cfg)
    try:
        result = PipelineService.run_sync(pipeline, ctx)
        console.print(f"[green]✓[/green] Output: [bold]{result.output_dir}[/bold]")
    except Exception as e:
        console.print(f"[red]✗[/red] Pipeline failed: {e}")
        raise typer.Exit(1)


@app.command()
def summarize(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file (YAML)"),
) -> None:
    """Generate summary only (video → scene → speech → llm)."""
    cfg = PipelineService.load_config(video, output, config,
                                       speech_provider="whisper",
                                       ocr_provider="none", vision_provider="none")
    cfg["output_dir"] = str(output or video.parent / f"{video.stem}.summary")

    pipeline = PipelineService.build_partial_pipeline(["video", "scene", "speech", "llm"])
    ctx = PipelineService.create_context(str(video), cfg["output_dir"], cfg)
    with console.status("[bold cyan]Analyzing video…[/bold cyan]"):
        result = PipelineService.run_sync(pipeline, ctx)

    summary = result.llm_output.get("summary", "No summary generated.")
    console.print(f"\n[bold]Summary:[/bold]\n{summary}")


@app.command()
def transcript(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file (YAML)"),
) -> None:
    """Generate transcript only (video → speech)."""
    cfg = PipelineService.load_config(video, output, config, speech_provider="whisper")
    cfg["output_dir"] = str(output or video.parent / f"{video.stem}.transcript")

    pipeline = PipelineService.build_partial_pipeline(["video", "speech"])
    ctx = PipelineService.create_context(str(video), cfg["output_dir"], cfg)
    with console.status("[bold cyan]Transcribing video…[/bold cyan]"):
        result = PipelineService.run_sync(pipeline, ctx)

    text = result.transcript.get("text", "")
    segments = result.transcript.get("segments", [])
    if output:
        out_path = Path(cfg["output_dir"]) / "transcript.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"[green]✓[/green] Transcript saved: {out_path}")
    else:
        console.print(f"\n[bold]Transcript ({len(segments)} segments):[/bold]\n{text[:2000]}")


@app.command()
def run(
    stages: List[str] = typer.Argument(..., help="Stage names (video, scene, speech, ocr, vision, llm, embedding, search, render)"),
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Run specific pipeline stage(s) on a video."""
    known = set(PipelineService.STAGE_MAP)
    unknown = [s for s in stages if s not in known]
    if unknown:
        console.print(f"[red]Unknown stage(s):[/red] {', '.join(unknown)}")
        console.print(f"Available: {', '.join(sorted(known))}")
        raise typer.Exit(1)

    cfg = {"output_dir": str(output or video.parent / f"{video.stem}.run")}
    pipeline = PipelineService.build_partial_pipeline(stages)
    ctx = PipelineService.create_context(str(video), cfg["output_dir"], cfg)
    with console.status(f"[bold cyan]Running: {' → '.join(stages)}…[/bold cyan]"):
        result = PipelineService.run_sync(pipeline, ctx)
    console.print(f"[green]✓[/green] Stages completed. Output: {result.output_dir}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    index: Path = typer.Option(..., "--index", "-i", help="Path to search index", exists=True),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Number of results"),
) -> None:
    """Semantic search across processed videos."""
    from vdoc.search.engine import SearchEngine
    engine = SearchEngine()
    engine.load(str(index))
    results = engine.search(query, top_k=top_k)
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return
    console.print(f"[bold]Search results for:[/bold] {query}\n")
    for r in results:
        console.print(f"  [cyan]{r['id']}[/cyan] ({r['score']:.2f})")
        console.print(f"  {r['text'][:200]}\n")


@app.command()
def export(
    input_dir: Path = typer.Argument(..., help="MarkDirectory input", exists=True),
    format: str = typer.Option("markdown", "--format", "-f", help="Export format: markdown, json, html"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Export processed video to a different format."""
    from vdoc.services.export_service import ExportService
    out = str(output or input_dir.parent / f"{input_dir.stem}.{format}")
    ExportService.export(str(input_dir), format, out)
    console.print(f"[green]✓[/green] Exported to: {out}")


@app.command()
def plugin(
    list_plugins: bool = typer.Option(False, "--list", "-l", help="List all plugins"),
) -> None:
    """List and manage plugins."""
    from vdoc.plugins.loader import PluginLoader
    plugins = PluginLoader.list_plugins()
    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return
    console.print("[bold]Available Plugins:[/bold]\n")
    for name, desc in plugins.items():
        console.print(f"  [cyan]{name}[/cyan] — {desc}")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current config"),
    path: Optional[Path] = typer.Option(None, "--path", "-p", help="Config file path"),
    validate: bool = typer.Option(False, "--validate", "-v", help="Validate configuration"),
) -> None:
    """View and manage configuration."""
    cm = ConfigManager()
    if path:
        cm.load_yaml(path)
    if validate:
        from vdoc.config.validator import validate_config
        errors = validate_config(cm.to_dict())
        if errors:
            for e in errors:
                console.print(f"[red]✗[/red] {e}")
            raise typer.Exit(1)
        console.print("[green]✓[/green] Configuration valid")
    elif show:
        cfg = cm.resolve()
        console.print(json.dumps(cfg.model_dump(), indent=2))


@app.command()
def doctor() -> None:
    """Check system dependencies."""
    checks = [
        ("Python 3.10+", sys.version_info >= (3, 10)),
    ]
    checks.append(("FFmpeg", shutil.which("ffmpeg") is not None))
    import importlib.util
    for mod in ["cv2", "scenedetect", "PIL"]:
        checks.append((mod, importlib.util.find_spec(mod) is not None))

    console.print("[bold]System Check:[/bold]\n")
    for name, ok in checks:
        icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
        console.print(f"  {icon} {name}")


@app.command()
def benchmark(
    video: Path = typer.Argument(..., help="Video file for benchmarking", exists=True),
) -> None:
    """Run performance benchmarks."""
    from vdoc.services.benchmark_service import BenchmarkService
    results = BenchmarkService.run(str(video))
    console.print("[bold]Benchmark Results:[/bold]\n")
    for name, duration in results:
        console.print(f"  {name}: {duration:.2f}s")


@app.command()
def validate(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file (YAML)"),
) -> None:
    """Validate that a video can be processed with current config."""
    from vdoc.config.validator import validate_config
    cfg = PipelineService.load_config(video, video.parent / f"{video.stem}.markdir", config)
    errors = validate_config(cfg)
    if errors:
        console.print("[red]Configuration errors:[/red]")
        for e in errors:
            console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(1)
    console.print("[green]✓[/green] Configuration valid")
    console.print(f"  Video: {video.name} ({video.stat().st_size / 1e6:.1f} MB)")
    console.print(f"  LLM: {cfg.get('llm_provider')} / {cfg.get('llm_model')}")
    console.print(f"  Speech: {cfg.get('speech_provider')}")
    console.print(f"  Output: {cfg.get('output_format')}")


@app.command()
def completion(shell: str = typer.Argument("bash", help="Shell type: bash, zsh, fish, powershell")) -> None:
    """Generate shell completion scripts."""
    from typer.main import get_command
    cmd = get_command(app)
    console.print(cmd.shell_complete(shell))


if __name__ == "__main__":
    app()
