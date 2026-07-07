"""JSON renderer — exports VideoDocument as structured JSON."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from videomarker.models.document import VideoDocument
from videomarker.renderers.base import BaseRenderer


class JSONRenderer(BaseRenderer):
    """Export VideoDocument as a single JSON file."""

    format_name = "json"

    def render(self, doc: VideoDocument, output_dir: Path) -> Path:
        data = self._to_dict(doc)
        path = output_dir / "document.json"
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return path

    def _to_dict(self, doc: VideoDocument) -> dict:
        return {
            "title": doc.title,
            "source": str(doc.source_path),
            "duration": doc.duration,
            "fps": doc.fps,
            "resolution": {"width": doc.resolution[0], "height": doc.resolution[1]},
            "codec": doc.codec,
            "file_size": doc.file_size,
            "summary": doc.summary,
            "keywords": doc.keywords,
            "scenes": [
                {
                    "id": s.id,
                    "number": s.number,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "description": s.description,
                    "transcript": s.transcript.text if s.transcript else None,
                    "ocr": s.ocr.text if s.ocr else None,
                    "caption": s.caption.detailed if s.caption else None,
                }
                for s in doc.timeline.scenes
            ],
            "chapters": doc.timeline.chapters,
            "concepts": [
                {"name": c.name, "description": c.description, "importance": c.importance}
                for c in doc.concepts
            ],
            "entities": [
                {"name": e.name, "type": e.type, "confidence": e.confidence}
                for e in doc.entities
            ],
        }
