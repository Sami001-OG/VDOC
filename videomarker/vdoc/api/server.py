"""VDOC REST API v1 — FastAPI server using the service layer."""

from __future__ import annotations

import json
import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from vdoc.services import PipelineService, ProviderService
from vdoc.services.export_service import ExportService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="VDOC API",
    description="Convert videos to structured MarkDirectory format",
    version="1.0.0",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_jobs: Dict[str, Dict[str, Any]] = {}


def create_app() -> FastAPI:
    return app


@app.on_event("startup")
async def startup() -> None:
    ProviderService.register_defaults()
    logger.info("VDOC API v1 started")


# --- Health (#80) ---

@app.get("/v1/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "providers": ProviderService.list_available(),
    }


# --- Process (#71) ---

@app.post("/v1/process")
async def process_video(
    file: UploadFile = File(..., description="Video file to process"),
    config: Optional[str] = Form(None, description="JSON configuration overrides"),
) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())[:8]
    temp_dir = Path(tempfile.gettempdir()) / f"vdoc_{job_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    video_path = temp_dir / (file.filename or "video.mp4")
    content = await file.read()
    video_path.write_bytes(content)

    cfg = PipelineService.load_config(
        video_path, temp_dir / f"{Path(file.filename or 'video').stem}.markdir"
    )
    if config:
        cfg.update(json.loads(config))

    _jobs[job_id] = {
        "id": job_id,
        "status": "processing",
        "video": file.filename,
        "video_path": str(video_path),
    }

    try:
        pipeline = PipelineService.build_pipeline(cfg)
        ctx = PipelineService.create_context(str(video_path), cfg["output_dir"], cfg)
        result = await PipelineService.run_pipeline(pipeline, ctx)
        _jobs[job_id].update({"status": "completed", "errors": ctx.errors, "output_dir": result.output_dir})
    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)
        logger.exception("Job %s failed", job_id)

    return _jobs[job_id]


# --- Status ---

@app.get("/v1/status/{job_id}")
async def get_status(job_id: str) -> Dict[str, Any]:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# --- Search ---

@app.post("/v1/search")
async def search_video(
    job_id: str = Form(...),
    query: str = Form(...),
    top_k: int = Form(10),
) -> List[Dict[str, Any]]:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not yet completed")

    from vdoc.search.engine import SearchEngine
    search_path = Path(job["output_dir"]) / "search.index"
    if not search_path.exists():
        raise HTTPException(status_code=404, detail="Search index not found")

    engine = SearchEngine()
    engine.load(str(search_path))
    return engine.search(query, top_k=top_k)


# --- Scene ---

@app.get("/v1/scene/{job_id}/{scene_number}")
async def get_scene(job_id: str, scene_number: int) -> Dict[str, Any]:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    scene_dir = Path(job.get("output_dir", "")) / "scenes" / f"scene_{scene_number:03d}"
    if not scene_dir.exists():
        raise HTTPException(status_code=404, detail="Scene not found")
    result: Dict[str, Any] = {"scene_number": scene_number, "files": {}}
    for f in scene_dir.iterdir():
        if f.suffix in (".md", ".json", ".txt"):
            result["files"][f.name] = f.read_text(encoding="utf-8")
        elif f.suffix == ".jpg":
            result["files"][f.name] = str(f)
    meta_path = scene_dir / "metadata.json"
    if meta_path.exists():
        result["metadata"] = json.loads(meta_path.read_text(encoding="utf-8"))
    return result


# --- Summary ---

@app.get("/v1/summary/{job_id}")
async def get_summary(job_id: str) -> str:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    summary_path = Path(job["output_dir"]) / "summary.md"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary_path.read_text(encoding="utf-8")


# --- Timeline ---

@app.get("/v1/timeline/{job_id}")
async def get_timeline(job_id: str) -> Dict[str, Any]:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    timeline_path = Path(job["output_dir"]) / "timeline.json"
    if not timeline_path.exists():
        raise HTTPException(status_code=404, detail="Timeline not found")
    return json.loads(timeline_path.read_text(encoding="utf-8"))


# --- Download ---

@app.get("/v1/download/{job_id}")
async def download(job_id: str) -> FileResponse:
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    output_dir = Path(job["output_dir"])
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output not found")
    zip_path = Path(tempfile.gettempdir()) / f"{job_id}.zip"
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", output_dir)
    return FileResponse(zip_path, media_type="application/zip", filename=f"{output_dir.name}.zip")


# --- Processors ---

@app.get("/v1/processors")
async def list_processors() -> List[Dict[str, Any]]:
    from vdoc.plugins.loader import PluginLoader
    plugins = PluginLoader.list_plugins()
    return [{"name": k, "description": v} for k, v in plugins.items()]
