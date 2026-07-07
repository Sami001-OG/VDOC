"""MarkDirectory renderer — produces the structured output directory."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from videomarker.models.document import VideoDocument
from videomarker.renderers.base import BaseRenderer


class MarkDirectoryRenderer(BaseRenderer):
    """Render VideoDocument as a structured MarkDirectory.

    video.markdir/
    ├── metadata.json
    ├── timeline.json
    ├── manifest.json
    ├── summary.md
    ├── chapters.md
    ├── transcript.md
    ├── frames/
    ├── assets/
    ├── thumbnails/
    ├── embeddings/
    ├── search/
    └── scenes/
        └── scene_001/
            ├── metadata.json
            ├── transcript.md
            ├── caption.md
            ├── ocr.md
            ├── keyframe.jpg
            └── embedding.bin
    """

    format_name = "markdirectory"

    def render(self, doc: VideoDocument, output_dir: Path) -> Path:
        output_dir = output_dir / f"{doc.source_path.stem}.markdir"
        if output_dir.exists():
            shutil.rmtree(output_dir)

        # Create directory structure
        dirs = self._create_structure(output_dir)
        self._write_metadata(doc, dirs)
        self._write_timeline(doc, dirs)
        self._write_manifest(doc, dirs)
        self._write_summary(doc, dirs)
        self._write_chapters(doc, dirs)
        self._write_transcript(doc, dirs)
        self._write_scenes(doc, dirs)
        self._copy_assets(doc, dirs)
        return output_dir

    def _create_structure(self, root: Path) -> Dict[str, Path]:
        dirs = {
            "root": root,
            "scenes": root / "scenes",
            "frames": root / "frames",
            "assets": root / "assets",
            "thumbnails": root / "thumbnails",
            "embeddings": root / "embeddings",
            "search": root / "search",
        }
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)
        return dirs

    def _write_metadata(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        data = {
            "title": doc.title,
            "source": str(doc.source_path),
            "duration": doc.duration,
            "fps": doc.fps,
            "resolution": {"width": doc.resolution[0], "height": doc.resolution[1]},
            "codec": doc.codec,
            "file_size": doc.file_size,
            "scenes": doc.scene_count,
            "chapters": doc.chapter_count,
            "created_at": doc.created_at.isoformat(),
        }
        (dirs["root"] / "metadata.json").write_text(json.dumps(data, indent=2))

    def _write_timeline(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        data = {
            "duration": doc.duration,
            "scenes": [
                {
                    "id": s.id,
                    "number": s.number,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "description": s.description,
                }
                for s in doc.timeline.scenes
            ],
            "chapters": doc.timeline.chapters,
        }
        (dirs["root"] / "timeline.json").write_text(json.dumps(data, indent=2))

    def _write_manifest(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        manifest = {
            "version": "0.1.0",
            "created_at": doc.created_at.isoformat(),
            "video": doc.source_path.name,
            "duration": doc.duration,
            "scenes": doc.scene_count,
            "chapters": doc.chapter_count,
            "has_transcript": bool(doc.transcript.text),
            "has_embeddings": len(doc.embeddings) > 0,
            "has_ocr": any(s.ocr for s in doc.timeline.scenes),
        }
        (dirs["root"] / "manifest.json").write_text(json.dumps(manifest, indent=2))

    def _write_summary(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        content = f"# Summary\n\n{doc.summary}\n\n## Keywords\n\n"
        for kw in doc.keywords:
            content += f"- {kw}\n"
        (dirs["root"] / "summary.md").write_text(content)

    def _write_chapters(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        content = "# Chapters\n\n"
        for ch in doc.timeline.chapters:
            content += f"## {ch.get('title', 'Untitled')}\n"
            content += f"- **Time**: {ch.get('start_time', 0):.1f}s – {ch.get('end_time', 0):.1f}s\n"
            content += f"- **Scenes**: {len(ch.get('scene_ids', []))}\n\n"
        (dirs["root"] / "chapters.md").write_text(content)

    def _write_transcript(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        content = "# Transcript\n\n"
        for seg in doc.transcript.segments:
            ts = f"[{seg['start']:.1f}s - {seg['end']:.1f}s]"
            content += f"{ts} {seg['text']}\n\n"
        (dirs["root"] / "transcript.md").write_text(content or "No transcript available.")

    def _write_scenes(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        for scene in doc.timeline.scenes:
            scene_dir = dirs["scenes"] / f"scene_{scene.number:03d}"
            scene_dir.mkdir(exist_ok=True)

            # Metadata
            meta = {
                "number": scene.number,
                "start_time": scene.start_time,
                "end_time": scene.end_time,
                "duration": scene.duration,
                "description": scene.description,
            }
            (scene_dir / "metadata.json").write_text(json.dumps(meta, indent=2))

            # Transcript
            if scene.transcript:
                (scene_dir / "transcript.md").write_text(scene.transcript.text)

            # Caption
            if scene.caption:
                (scene_dir / "caption.md").write_text(scene.caption.detailed)

            # OCR
            if scene.ocr:
                (scene_dir / "ocr.md").write_text(scene.ocr.text)

            # Keyframe
            if scene.keyframe_path and scene.keyframe_path.exists():
                shutil.copy2(scene.keyframe_path, scene_dir / "keyframe.jpg")

            # Embedding
            if scene.embedding:
                import struct
                path = scene_dir / "embedding.bin"
                path.write_bytes(struct.pack(f"{len(scene.embedding.vector)}f", *scene.embedding.vector))

    def _copy_assets(self, doc: VideoDocument, dirs: Dict[str, Path]) -> None:
        for asset in doc.assets:
            if asset.path.exists():
                dest = dirs["assets"] / asset.path.name
                shutil.copy2(asset.path, dest)
