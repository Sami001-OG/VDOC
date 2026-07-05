"""HTML renderer — produces a single-page HTML report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from videomarker.models.document import VideoDocument
from videomarker.renderers.base import BaseRenderer


class HTMLRenderer(BaseRenderer):
    """Render VideoDocument as a self-contained HTML page."""

    format_name = "html"

    def render(self, doc: VideoDocument, output_dir: Path) -> Path:
        html = self._build_html(doc)
        path = output_dir / "report.html"
        path.write_text(html, encoding="utf-8")
        return path

    def _build_html(self, doc: VideoDocument) -> str:
        scenes_html = ""
        for scene in doc.timeline.scenes:
            scenes_html += f"""
            <div class="scene">
                <h3>Scene {scene.number} <span class="time">{scene.start_time:.1f}s – {scene.end_time:.1f}s</span></h3>
                {f'<p class="desc">{scene.description}</p>' if scene.description else ''}
                {f'<div class="transcript">{scene.transcript.text}</div>' if scene.transcript else ''}
                {f'<div class="ocr">{scene.ocr.text}</div>' if scene.ocr else ''}
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{doc.title or doc.source_path.name}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0b0e; color: #e8e9ed; padding: 2rem; }}
.container {{ max-width: 900px; margin: 0 auto; }}
h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
.meta {{ color: #5c5e66; font-size: 0.9rem; margin-bottom: 2rem; }}
.summary {{ background: #121318; border: 1px solid #1e1f27; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; }}
.scene {{ background: #121318; border: 1px solid #1e1f27; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; }}
.scene h3 {{ margin-bottom: 0.5rem; }}
.time {{ color: #22d3ee; font-size: 0.85rem; font-weight: 400; }}
.desc {{ color: #94969e; margin-bottom: 0.5rem; }}
.transcript {{ border-left: 2px solid #22d3ee; padding-left: 1rem; margin-top: 0.5rem; color: #94969e; }}
.ocr {{ border-left: 2px solid #8b5cf6; padding-left: 1rem; margin-top: 0.5rem; color: #94969e; font-family: monospace; }}
</style>
</head>
<body>
<div class="container">
<h1>{doc.title or doc.source_path.name}</h1>
<p class="meta">{doc.duration:.1f}s · {doc.resolution[0]}×{doc.resolution[1]} · {doc.codec} · {doc.scene_count} scenes</p>
{f'<div class="summary">{doc.summary}</div>' if doc.summary else ''}
{scenes_html}
</div>
</body>
</html>"""
