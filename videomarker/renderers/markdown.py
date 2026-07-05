"""Markdown renderer — produces a single comprehensive Markdown document."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from videomarker.models.document import VideoDocument
from videomarker.renderers.base import BaseRenderer


class MarkdownRenderer(BaseRenderer):
    """Render VideoDocument as a single Markdown file."""

    format_name = "markdown"

    def render(self, doc: VideoDocument, output_dir: Path) -> Path:
        md = self._render_header(doc)
        md += self._render_timeline(doc)
        md += self._render_transcript(doc)
        md += self._render_ocr(doc)
        md += self._render_concepts(doc)
        return self._write(output_dir, "README.md", md)

    def _render_header(self, doc: VideoDocument) -> str:
        lines = [
            f"# {doc.title or doc.source_path.name}",
            "",
            f"- **Duration**: {doc.duration:.1f}s",
            f"- **Resolution**: {doc.resolution[0]}×{doc.resolution[1]}",
            f"- **Codec**: {doc.codec}",
            f"- **Scenes**: {doc.scene_count}",
            "",
            "---",
            "",
        ]
        if doc.summary:
            lines += ["## Summary", "", doc.summary, "", "---", ""]
        return "\n".join(lines)

    def _render_timeline(self, doc: VideoDocument) -> str:
        lines = ["## Timeline", ""]
        for scene in doc.timeline.scenes:
            lines.append(f"### Scene {scene.number} ({scene.start_time:.1f}s - {scene.end_time:.1f}s)")
            if scene.description:
                lines.append(f"{scene.description}")
            if scene.transcript:
                lines.append(f"> {scene.transcript.text[:200]}…")
            lines.append("")
        return "\n".join(lines)

    def _render_transcript(self, doc: VideoDocument) -> str:
        if not doc.transcript.text:
            return ""
        lines = ["## Transcript", ""]
        for seg in doc.transcript.segments:
            ts = f"[{seg['start']:.1f}s - {seg['end']:.1f}s]"
            lines.append(f"{ts} {seg['text']}")
            lines.append("")
        return "\n".join(lines)

    def _render_ocr(self, doc: VideoDocument) -> str:
        parts = []
        for scene in doc.timeline.scenes:
            if scene.ocr and scene.ocr.text:
                parts.append(f"### Scene {scene.number} OCR\n\n{scene.ocr.text}\n")
        if not parts:
            return ""
        return "## OCR Text\n\n" + "\n".join(parts)

    def _render_concepts(self, doc: VideoDocument) -> str:
        if not doc.concepts:
            return ""
        lines = ["## Key Concepts", ""]
        for c in doc.concepts:
            lines.append(f"- **{c.name}**: {c.description}")
        return "\n".join(lines)

    def _write(self, output_dir: Path, filename: str, content: str) -> Path:
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        return path
