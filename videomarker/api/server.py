"""VideoMarker REST API — FastAPI-based server for video processing."""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from videomarker.config.settings import VideoMarkerSettings, load_settings
from videomarker.core.pipeline import Pipeline
from videomarker.core.plugin import PluginRegistry

logger = logging.getLogger(__name__)

app = FastAPI(
    title="VideoMarker API",
    description="Convert videos to structured MarkDirectory format",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
_jobs: Dict[str, Dict[str, Any]] = {}
_settings: Optional[VideoMarkerSettings] = None


def get_settings() -> VideoMarkerSettings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def create_app(settings: Optional[VideoMarkerSettings] = None) -> FastAPI:
    """Create and configure the FastAPI app with optional custom settings."""
    global _settings
    if settings:
        _settings = settings
    return app


@app.on_event("startup")
async def startup() -> None:
    """Initialize plugin system on startup."""
    PluginRegistry.discover()
    logger.info("VideoMarker API started with %d processors", len(PluginRegistry.get_all_plugins()))


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/process")
async def process_video(
    file: UploadFile = File(..., description="Video file to process"),
    config: Optional[str] = Form(None, description="JSON configuration overrides"),
) -> Dict[str, Any]:
    """Upload and start processing a video file."""
    job_id = str(uuid.uuid4())[:8]

    # Save uploaded file
    temp_dir = Path(get_settings().temp_dir or "temp") / job_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    video_path = temp_dir / file.filename  # type: ignore
    content = await file.read()
    video_path.write_bytes(content)

    # Apply config overrides if provided
    settings = get_settings()
    if config:
        try:
            overrides = json.loads(config)
            for key, value in overrides.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON configuration")

    # Start processing
    _jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "video": file.filename,
        "video_path": str(video_path),
        "output_path": str(temp_dir / f"{Path(file.filename).stem}.markdir"),
    }

    try:
        output_dir = Path(temp_dir / f"{Path(file.filename).stem}.markdir")
        pipeline = Pipeline(settings=settings)
        context = pipeline.run(video_path, output_dir=output_dir)

        _jobs[job_id].update({
            "status": "completed" if not context.errors else "completed_with_errors",
            "errors": context.errors,
            "output_path": str(output_dir),
        })
    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)
        logger.error("Job %s failed: %s", job_id, e)

    return _jobs[job_id]


@app.get("/status/{job_id}")
async def get_status(job_id: str) -> Dict[str, Any]:
    """Get the status of a processing job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/search")
async def search_video(
    job_id: str = Form(...),
    query: str = Form(...),
    top_k: int = Form(10),
) -> List[Dict[str, Any]]:
    """Search within a processed video's content."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] not in ("completed", "completed_with_errors"):
        raise HTTPException(status_code=400, detail="Job not yet completed")

    from videomarker.search.embeddings import EmbeddingGenerator, SearchEngine

    search_index_path = Path(job["output_path"]) / "embeddings" / "search_index.json"
    if not search_index_path.exists():
        raise HTTPException(status_code=404, detail="Search index not found")

    engine = SearchEngine()
    engine.load(search_index_path)
    generator = EmbeddingGenerator()
    results = engine.search(query, top_k=top_k, generator=generator)

    return [r.model_dump() for r in results]


@app.get("/scene/{job_id}/{scene_number}")
async def get_scene(job_id: str, scene_number: int) -> Dict[str, Any]:
    """Get scene data by scene number."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    scene_dir = Path(job["output_path"]) / "scenes" / f"scene_{scene_number:03d}"
    if not scene_dir.exists():
        raise HTTPException(status_code=404, detail="Scene not found")

    result: Dict[str, Any] = {"scene_number": scene_number, "files": {}}
    for f in scene_dir.iterdir():
        if f.suffix in (".md", ".json", ".jpg", ".bin"):
            result["files"][f.name] = f.read_text(encoding="utf-8") if f.suffix != ".jpg" else str(f)

    # Also read metadata
    meta_path = scene_dir / "metadata.json"
    if meta_path.exists():
        result["metadata"] = json.loads(meta_path.read_text(encoding="utf-8"))

    return result


@app.get("/summary/{job_id}")
async def get_summary(job_id: str) -> str:
    """Get the video summary."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    summary_path = Path(job["output_path"]) / "summary.md"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Summary not found")

    return summary_path.read_text(encoding="utf-8")


@app.get("/timeline/{job_id}")
async def get_timeline(job_id: str) -> Dict[str, Any]:
    """Get the video timeline."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    timeline_path = Path(job["output_path"]) / "timeline.json"
    if not timeline_path.exists():
        raise HTTPException(status_code=404, detail="Timeline not found")

    return json.loads(timeline_path.read_text(encoding="utf-8"))


@app.get("/download/{job_id}")
async def download(job_id: str) -> FileResponse:
    """Download the complete MarkDirectory as a ZIP file."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    output_dir = Path(job["output_path"])
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output not found")

    import shutil
    import tempfile

    zip_path = Path(tempfile.gettempdir()) / f"{job_id}.zip"
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", output_dir)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{output_dir.name}.zip",
    )


@app.get("/processors")
async def list_processors() -> List[Dict[str, Any]]:
    """List all available processor plugins."""
    PluginRegistry.discover()
    return [
        {
            "name": p.name,
            "dependencies": p.dependencies,
            "priority": p.priority,
        }
        for p in PluginRegistry.get_all_plugins()
    ]
