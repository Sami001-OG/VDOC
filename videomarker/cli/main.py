"""VDOC CLI — complete command-line interface.

Commands:
    vdoc process     Process a video into MarkDirectory
    vdoc summarize   Generate summary only
    vdoc transcript  Generate transcript only
    vdoc search      Semantic search across processed videos
    vdoc export      Export processed video to format
    vdoc plugin      List and manage plugins
    vdoc config      View and manage configuration
    vdoc doctor      Check system dependencies
    vdoc benchmark   Run performance benchmarks
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from videomarker.config.manager import ConfigManager
from videomarker.models.document import VideoDocument
from videomarker.pipeline.orchestrator import PipelineOrchestrator
from videomarker.pipeline.stages import (
    VideoStage,
    SceneDetectionStage,
    SpeechStage,
    OCRStage,
    VisionStage,
    LLMStage,
    RenderStage,
)
from videomarker.providers.registry import ProviderRegistry
from videomarker.providers.llm.openai_compatible import OpenAICompatibleProvider
from videomarker.providers.speech.whisper import WhisperSpeechProvider
from videomarker.providers.vision.openai_vision import OpenAIVisionProvider
from videomarker.providers.ocr.paddle import PaddleOCRProvider
from videomarker.providers.embedding.sentence import SentenceEmbeddingProvider

app = typer.Typer(name="vdoc", help="Video → Document. Structured. Searchable. Semantic.")
console = Console()

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])


def _register_default_providers(config: Dict[str, Any]) -> None:
    """Register all default providers based on configuration."""
    if not ProviderRegistry.is_registered("video"):
        from videomarker.providers.video.ffmpeg import FFmpegVideoProvider
        ProviderRegistry.register("video", FFmpegVideoProvider)

    if not ProviderRegistry.is_registered("llm"):
        ProviderRegistry.register("llm", OpenAICompatibleProvider)

    if not ProviderRegistry.is_registered("speech"):
        ProviderRegistry.register("speech", WhisperSpeechProvider)

    if not ProviderRegistry.is_registered("vision"):
        ProviderRegistry.register("vision", OpenAIVisionProvider)

    if not ProviderRegistry.is_registered("ocr"):
        ProviderRegistry.register("ocr", PaddleOCRProvider)

    if not ProviderRegistry.is_registered("embedding"):
        ProviderRegistry.register("embedding", SentenceEmbeddingProvider)


def _build_pipeline(config: Dict[str, Any]) -> PipelineOrchestrator:
    """Build and return the processing pipeline."""
    pipeline = PipelineOrchestrator()
    pipeline \
        .register_stage(VideoStage()) \
        .register_stage(SceneDetectionStage()) \
        .register_stage(SpeechStage()) \
        .register_stage(OCRStage()) \
        .register_stage(VisionStage()) \
        .register_stage(LLMStage()) \
        .register_stage(RenderStage())

    if config.get("output_dir"):
        pipeline.set_checkpoint_dir(Path(config["output_dir"]) / ".checkpoints")

    return pipeline


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
    # Load config
    cm = ConfigManager()
    cm.load_yaml(config)
    cm.load_cli(
        video_path=str(video),
        output_dir=str(output or video.parent / f"{video.stem}.markdir"),
        overwrite=overwrite,
        speech_provider="none" if no_transcript else None,
        ocr_provider="none" if no_ocr else None,
        vision_provider="none" if no_vision else None,
        llm_provider="none" if no_llm else None,
    )
    cfg = cm.resolve()
    cfg_dict = cfg.model_dump()

    console.print(f"[bold cyan]VDOC[/bold cyan] Processing: [white]{video.name}[/white]")

    # Register providers
    _register_default_providers(cfg_dict)

    # Run pipeline
    async def run() -> None:
        pipeline = _build_pipeline(cfg_dict)

        ctx = pipeline._make_context()
        ctx.video_path = str(video)
        ctx.output_dir = cfg_dict.get("output_dir", str(video.parent / f"{video.stem}.markdir"))
        ctx.config = cfg_dict

        try:
            result = await pipeline.run(ctx, resume_from="video" if resume else None)
            console.print(f"[green]✓[/green] Output: [bold]{result.output_dir}[/bold]")
        except Exception as e:
            console.print(f"[red]✗[/red] Pipeline failed: {e}")
            raise typer.Exit(1)
        finally:
            await ProviderRegistry.close_all()

    asyncio.run(run())


@app.command()
def summarize(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Generate summary only."""
    console.print("[yellow]Summary mode[/yellow]")
    # TODO: implement summary-only mode


@app.command()
def transcript(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Generate transcript only."""
    console.print("[yellow]Transcript mode[/yellow]")
    # TODO: implement transcript-only mode


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    index: Path = typer.Option(..., "--index", "-i", help="Path to search index", exists=True),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Number of results"),
) -> None:
    """Semantic search across processed videos."""
    from videomarker.search.engine import SearchEngine

    engine = SearchEngine()
    engine.load(str(index))
    results = engine.search(query, top_k=top_k)

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    console.print(f"[bold]Search results for:[/bold] {query}\n")
    for r in results:
        console.print(f"  [cyan]{r['id']}[/cyan] ({r['score']:.2f})")
        console.print(f"  {r['text'][:200]}…")
        console.print()


@app.command()
def export(
    input_dir: Path = typer.Argument(..., help="MarkDirectory input", exists=True),
    format: str = typer.Option("markdown", "--format", "-f", help="Export format: markdown, json, html"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """Export processed video to a different format."""
    console.print(f"[yellow]Exporting to {format}…[/yellow]")
    # TODO: implement export


@app.command()
def plugin(
    list_plugins: bool = typer.Option(False, "--list", "-l", help="List all plugins"),
) -> None:
    """List and manage plugins."""
    from videomarker.plugins.loader import PluginLoader

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
) -> None:
    """View and manage configuration."""
    cm = ConfigManager()
    if path:
        cm.load_yaml(path)
    cfg = cm.resolve()
    if show:
        console.print(json.dumps(cfg.model_dump(), indent=2))


@app.command()
def doctor() -> None:
    """Check system dependencies."""
    checks = [
        ("Python 3.10+", sys.version_info >= (3, 10)),
    ]

    # Check ffmpeg
    import shutil
    checks.append(("FFmpeg", shutil.which("ffmpeg") is not None))

    # Check imports
    import importlib.util
    for mod in ["cv2", "scenedetect", "PIL"]:
        checks.append((f"{mod}", importlib.util.find_spec(mod) is not None))

    console.print("[bold]System Check:[/bold]\n")
    for name, ok in checks:
        icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
        console.print(f"  {icon} {name}")


@app.command()
def benchmark(
    video: Path = typer.Argument(..., help="Video file for benchmarking", exists=True),
) -> None:
    """Run performance benchmarks."""
    console.print("[yellow]Benchmark mode[/yellow]")
    # TODO: implement benchmark


if __name__ == "__main__":
    app()
