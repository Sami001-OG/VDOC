"""MarkDirectory Renderer — produces the complete structured output directory."""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from videomarker.config.settings import VideoMarkerSettings
from videomarker.core.renderer import Renderer
from videomarker.models.markdirectory import Manifest, SceneDir
from videomarker.models.segment import Chapter, Scene, Timeline
from videomarker.models.transcript import Transcript
from videomarker.search.embeddings import Embedding, EmbeddingGenerator, SearchEngine

logger = logging.getLogger(__name__)


class MarkDirectoryRenderer(Renderer):
    """Renders pipeline output to the MarkDirectory format.

    Produces a structured directory with Markdown, JSON, images,
    embeddings, and a manifest.
    """

    def __init__(self, settings: Optional[VideoMarkerSettings] = None) -> None:
        super().__init__(settings)
        self._scene_dirs: List[SceneDir] = []

    def render(self, context: Any) -> Path:
        """Render all pipeline data into the MarkDirectory."""
        video_path = Path(context.data["video_path"])
        output_dir = context.output_dir or video_path.parent / f"{video_path.stem}.markdir"

        output_dir = Path(output_dir)
        if output_dir.exists() and self.settings and self.settings.overwrite:
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        scenes_dir = output_dir / "scenes"
        frames_dir = output_dir / "frames"
        assets_dir = output_dir / "assets"
        thumbnails_dir = output_dir / "thumbnails"
        subtitles_dir = output_dir / "subtitles"
        embeddings_dir = output_dir / "embeddings"

        for d in [scenes_dir, frames_dir, assets_dir, thumbnails_dir, subtitles_dir, embeddings_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Collect data
        video_info = context.video_info
        timeline: Optional[Timeline] = context.data.get("timeline")
        transcript: Optional[Transcript] = context.data.get("transcript")
        semantic = context.data.get("semantic")
        keywords = context.data.get("keywords", [])
        knowledge_graph = context.data.get("knowledge_graph")
        ocr_results = context.data.get("ocr_results", {})
        vision_results = context.data.get("vision_results", {})

        # Render components
        self._render_metadata(output_dir, video_info)
        self._render_transcript(output_dir, transcript, timeline)
        self._render_summary(output_dir, semantic)
        self._render_chapters(output_dir, timeline)
        self._render_timeline(output_dir, timeline)
        self._render_keywords(output_dir, keywords)
        self._render_entities(output_dir, knowledge_graph)
        self._render_scenes(scenes_dir, timeline, video_path, context)
        self._render_search_index(embeddings_dir, context)
        self._render_manifest(output_dir, video_path, context)

        logger.info("MarkDirectory rendered to %s", output_dir)
        return output_dir

    def render_scene(self, scene: Scene, context: Any) -> Path:
        """Render a single scene directory."""
        output_dir = Path(context.output_dir) / "scenes" / scene.id
        output_dir.mkdir(parents=True, exist_ok=True)

        scene_dir = SceneDir(
            scene_number=scene.scene_number,
            path=output_dir,
        )

        # Write metadata
        metadata = {
            "scene_number": scene.scene_number,
            "start_time": scene.start_time,
            "end_time": scene.end_time,
            "start_timestamp": scene.start_timestamp,
            "end_timestamp": scene.end_timestamp,
            "duration": scene.duration,
            "description": scene.description,
            "type": scene.segment_type.value,
        }
        meta_path = output_dir / "metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        scene_dir.metadata_json = meta_path

        # Write transcript for this scene
        transcript = context.data.get("transcript")
        if transcript:
            scene_transcript = self._get_scene_transcript(scene, transcript)
            if scene_transcript:
                trans_path = output_dir / "transcript.md"
                trans_path.write_text(scene_transcript, encoding="utf-8")
                scene_dir.transcript_md = trans_path

        # Write caption
        vision = context.data.get("vision_results", {}).get(scene.id)
        if vision and vision.description:
            caption_path = output_dir / "caption.md"
            caption_path.write_text(vision.description.detailed, encoding="utf-8")
            scene_dir.caption_md = caption_path

        # Write summary
        caption_path = output_dir / "summary.md"
        caption_path.write_text(scene.description or f"Scene {scene.scene_number}", encoding="utf-8")
        scene_dir.summary_md = caption_path

        # Write OCR
        ocr = context.data.get("ocr_results", {}).get(scene.id)
        if ocr and ocr.full_text:
            ocr_path = output_dir / "ocr.md"
            ocr_path.write_text(ocr.full_text, encoding="utf-8")
            scene_dir.ocr_md = ocr_path

        # Copy keyframe
        if scene.keyframe_path:
            kf_dest = output_dir / "keyframe.jpg"
            shutil.copy2(scene.keyframe_path, kf_dest)
            scene_dir.keyframe_jpg = kf_dest

        self._scene_dirs.append(scene_dir)
        return output_dir

    def _render_metadata(self, output_dir: Path, video_info: Any) -> None:
        """Write metadata.json."""
        if not video_info:
            return

        metadata = {
            "file": str(video_info.metadata.file_path),
            "file_size": video_info.metadata.file_size,
            "duration": video_info.metadata.duration,
            "fps": video_info.metadata.fps,
            "resolution": {
                "width": video_info.metadata.width,
                "height": video_info.metadata.height,
            },
            "codec": video_info.metadata.codec,
            "audio_codec": video_info.metadata.audio_codec,
            "bit_rate": video_info.metadata.bit_rate,
            "rotation": video_info.metadata.rotation,
            "format": video_info.metadata.format_name,
            "has_audio": video_info.metadata.has_audio,
            "title": video_info.metadata.title,
            "total_frames": video_info.total_frames,
        }
        path = output_dir / "metadata.json"
        path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _render_transcript(
        self, output_dir: Path, transcript: Optional[Transcript], timeline: Optional[Timeline]
    ) -> None:
        """Write transcript.md with speaker labels and timestamps."""
        if not transcript:
            (output_dir / "transcript.md").write_text("No transcript available.", encoding="utf-8")
            return

        md_lines: List[str] = ["# Transcript\n"]
        for seg in transcript.segments:
            speaker_label = f"**{seg.speaker_id}**" if seg.speaker_id else ""
            timestamp = f"[{seg.start:.1f}s - {seg.end:.1f}s]"
            line = f"{timestamp} {speaker_label}: {seg.text}"
            md_lines.append(line)
            md_lines.append("")

        path = output_dir / "transcript.md"
        path.write_text("\n".join(md_lines), encoding="utf-8")

        # Also write SRT subtitles
        self._write_srt(output_dir, transcript)

    def _write_srt(self, output_dir: Path, transcript: Transcript) -> None:
        """Write SRT subtitle file."""
        srt_lines: List[str] = []
        for i, seg in enumerate(transcript.segments, 1):
            start = self._srt_time(seg.start)
            end = self._srt_time(seg.end)
            srt_lines.append(str(i))
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(seg.text)
            srt_lines.append("")

        (output_dir / "subtitles" / "transcript.srt").write_text(
            "\n".join(srt_lines), encoding="utf-8"
        )

    def _srt_time(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _render_summary(self, output_dir: Path, semantic: Any) -> None:
        """Write summary.md."""
        md_lines: List[str] = ["# Summary\n"]
        if semantic:
            if semantic.overall_summary:
                md_lines.append(semantic.overall_summary)
                md_lines.append("")

            if semantic.topics:
                md_lines.append("## Topics\n")
                for topic in semantic.topics:
                    md_lines.append(f"### {topic.title}")
                    md_lines.append(topic.summary)
                    if topic.key_points:
                        md_lines.append("")
                        for point in topic.key_points:
                            md_lines.append(f"- {point}")
                    md_lines.append("")

        md_lines.append("_Generated by VideoMarker_")
        (output_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    def _render_chapters(self, output_dir: Path, timeline: Optional[Timeline]) -> None:
        """Write chapters.md."""
        md_lines: List[str] = ["# Chapters\n"]
        if timeline and timeline.chapters:
            for chapter in timeline.chapters:
                md_lines.append(
                    f"## {chapter.title}"
                    f"\n- **Time**: {chapter.start_timestamp} - {chapter.end_timestamp}"
                )
                if chapter.summary:
                    md_lines.append(f"- **Summary**: {chapter.summary}")
                md_lines.append(f"- **Scenes**: {', '.join(chapter.scene_ids)}")
                md_lines.append("")
        else:
            md_lines.append("No chapters detected.")

        (output_dir / "chapters.md").write_text("\n".join(md_lines), encoding="utf-8")

    def _render_timeline(self, output_dir: Path, timeline: Optional[Timeline]) -> None:
        """Write timeline.json."""
        if not timeline:
            (output_dir / "timeline.json").write_text("{}", encoding="utf-8")
            return

        data = {
            "duration": timeline.duration,
            "scenes": [
                {
                    "id": s.id,
                    "number": s.scene_number,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "start_timestamp": s.start_timestamp,
                    "end_timestamp": s.end_timestamp,
                    "description": s.description,
                }
                for s in timeline.scenes
            ],
            "chapters": [
                {
                    "id": c.id,
                    "number": c.chapter_number,
                    "title": c.title,
                    "start_time": c.start_time,
                    "end_time": c.end_time,
                    "start_timestamp": c.start_timestamp,
                    "end_timestamp": c.end_timestamp,
                    "scene_ids": c.scene_ids,
                }
                for c in timeline.chapters
            ],
        }
        (output_dir / "timeline.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

    def _render_keywords(self, output_dir: Path, keywords: List[str]) -> None:
        """Write keywords.md."""
        md_lines: List[str] = ["# Keywords\n"]
        for kw in keywords:
            md_lines.append(f"- {kw}")
        (output_dir / "keywords.md").write_text("\n".join(md_lines), encoding="utf-8")

    def _render_entities(self, output_dir: Path, knowledge_graph: Any) -> None:
        """Write entities.json."""
        if not knowledge_graph:
            (output_dir / "entities.json").write_text(
                json.dumps({"entities": {}, "relations": []}, indent=2),
                encoding="utf-8",
            )
            return

        data = {
            "entities": {
                name: {
                    "name": e.name,
                    "type": e.entity_type.value if hasattr(e.entity_type, 'value') else str(e.entity_type),
                    "description": e.description,
                    "confidence": e.confidence,
                }
                for name, e in knowledge_graph.entities.items()
            },
            "relations": [
                {
                    "source": r.source,
                    "target": r.target,
                    "relation": r.relation,
                    "evidence": r.evidence,
                }
                for r in knowledge_graph.relations
            ],
        }
        (output_dir / "entities.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _render_scenes(
        self,
        scenes_dir: Path,
        timeline: Optional[Timeline],
        video_path: Path,
        context: Any,
    ) -> None:
        """Render each scene as a subdirectory."""
        scenes = timeline.scenes if timeline else context.data.get("scenes", [])
        if not scenes:
            return

        for scene in scenes:
            self.render_scene(scene, context)

    def _render_search_index(
        self, embeddings_dir: Path, context: Any
    ) -> None:
        """Generate search index from transcript and scene data."""
        transcript = context.data.get("transcript")
        if not transcript:
            return

        embeddings_list: List[Embedding] = []
        generator = EmbeddingGenerator()

        # Embed each transcript segment
        texts = []
        for seg in transcript.segments:
            texts.append(seg.text)

        if texts:
            vectors = generator.generate(texts)
            for i, (seg, vec) in enumerate(zip(transcript.segments, vectors)):
                embeddings_list.append(
                    Embedding(
                        id=f"transcript_seg_{i:04d}",
                        vector=vec,
                        text=seg.text,
                        source_type="transcript",
                        timestamp=seg.start,
                    )
                )

        # Build and save search index
        engine = SearchEngine()
        engine.build_index(embeddings_list, generator)
        engine.save(embeddings_dir / "search_index.json")

        # Also save to root
        context.data.get("search_index", {})

    def _render_manifest(
        self, output_dir: Path, video_path: Path, context: Any
    ) -> None:
        """Write manifest.json describing the entire MarkDirectory."""
        video_info = context.video_info
        timeline = context.data.get("timeline")
        transcript = context.data.get("transcript")
        semantic = context.data.get("semantic")

        manifest = Manifest(
            video_file=video_path.name,
            duration=video_info.metadata.duration if video_info else 0.0,
            num_scenes=len(timeline.scenes) if timeline else 0,
            num_chapters=len(timeline.chapters) if timeline else 0,
            total_frames=video_info.total_frames if video_info else 0,
            has_transcript=transcript is not None,
            has_ocr=bool(context.data.get("ocr_results")),
            has_vision=bool(context.data.get("vision_results")),
            has_embeddings=True,
            has_knowledge_graph=context.data.get("knowledge_graph") is not None,
            pipeline_steps=list(context.status.keys()) if context.status else [],
        )

        (output_dir / "manifest.json").write_text(
            manifest.model_dump_json(indent=2), encoding="utf-8"
        )

    def _get_scene_transcript(self, scene: Scene, transcript: Transcript) -> Optional[str]:
        """Get transcript text relevant to a scene's time range."""
        segments = [
            seg for seg in transcript.segments
            if seg.start >= scene.start_time and seg.end <= scene.end_time
        ]
        if segments:
            return "\n".join(
                f"[{seg.start:.1f}s] {seg.speaker_id + ': ' if seg.speaker_id else ''}{seg.text}"
                for seg in segments
            )
        return None
