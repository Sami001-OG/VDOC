"""Timeline builder — constructs the structured timeline from scenes."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from videomarker.models.segment import Chapter, Scene, Timeline
from videomarker.models.video import VideoInfo

logger = logging.getLogger(__name__)


class TimelineBuilder:
    """Builds a structured timeline from detected scenes.

    Groups scenes into chapters, assigns sequential numbering,
    and constructs the complete Timeline object.
    """

    def build(
        self,
        scenes: List[Scene],
        video_info: Optional[VideoInfo] = None,
        chapter_boundaries: Optional[List[float]] = None,
    ) -> Timeline:
        """Build a complete timeline from scenes.

        Args:
            scenes: List of detected Scene objects.
            video_info: Optional video information for duration reference.
            chapter_boundaries: Optional timestamps for chapter grouping.

        Returns:
            A fully constructed Timeline.
        """
        timeline = Timeline()

        # Sort scenes by start time
        sorted_scenes = sorted(scenes, key=lambda s: s.start_time)

        for i, scene in enumerate(sorted_scenes):
            scene.scene_number = i + 1
            timeline.add_scene(scene)

        if video_info:
            timeline.duration = video_info.metadata.duration

        # Build chapters if boundaries are provided
        if chapter_boundaries and sorted_scenes:
            chapters = self._build_chapters(sorted_scenes, chapter_boundaries)
            for chapter in chapters:
                timeline.add_chapter(chapter)
        else:
            # Auto-generate chapters from scene grouping
            chapters = self._auto_chapterize(sorted_scenes)
            for chapter in chapters:
                timeline.add_chapter(chapter)

        logger.info(
            "Built timeline: %d scenes, %d chapters, %.1f seconds",
            len(timeline.scenes),
            len(timeline.chapters),
            timeline.duration,
        )

        return timeline

    def _build_chapters(
        self,
        scenes: List[Scene],
        boundaries: List[float],
    ) -> List[Chapter]:
        """Group scenes into chapters using provided boundary timestamps."""
        chapters: List[Chapter] = []
        boundary_idx = 0
        current_scenes: List[Scene] = []
        chapter_num = 0

        for scene in scenes:
            current_scenes.append(scene)
            if boundary_idx < len(boundaries) and scene.end_time >= boundaries[boundary_idx]:
                chapter_num += 1
                chapter = Chapter(
                    id=f"chapter_{chapter_num:03d}",
                    chapter_number=chapter_num,
                    title=f"Chapter {chapter_num}",
                    start_time=current_scenes[0].start_time,
                    end_time=scene.end_time,
                    scene_ids=[s.id for s in current_scenes],
                )
                chapters.append(chapter)
                current_scenes = []
                boundary_idx += 1

        # Remaining scenes as final chapter
        if current_scenes:
            chapter_num += 1
            chapter = Chapter(
                id=f"chapter_{chapter_num:03d}",
                chapter_number=chapter_num,
                title=f"Chapter {chapter_num}",
                start_time=current_scenes[0].start_time,
                end_time=current_scenes[-1].end_time,
                scene_ids=[s.id for s in current_scenes],
            )
            chapters.append(chapter)

        return chapters

    def _auto_chapterize(
        self,
        scenes: List[Scene],
        max_scenes_per_chapter: int = 8,
        max_gap_seconds: float = 30.0,
    ) -> List[Chapter]:
        """Automatically group scenes into chapters based on gaps and count."""
        if not scenes:
            return []

        chapters: List[Chapter] = []
        current_scenes: List[Scene] = [scenes[0]]
        chapter_num = 0

        for i in range(1, len(scenes)):
            gap = scenes[i].start_time - scenes[i - 1].end_time
            should_split = (
                len(current_scenes) >= max_scenes_per_chapter
                or gap > max_gap_seconds
            )

            if should_split:
                chapter_num += 1
                chapter = Chapter(
                    id=f"chapter_{chapter_num:03d}",
                    chapter_number=chapter_num,
                    title=f"Chapter {chapter_num}",
                    start_time=current_scenes[0].start_time,
                    end_time=current_scenes[-1].end_time,
                    scene_ids=[s.id for s in current_scenes],
                )
                chapters.append(chapter)
                current_scenes = [scenes[i]]
            else:
                current_scenes.append(scenes[i])

        # Final chapter
        if current_scenes:
            chapter_num += 1
            chapter = Chapter(
                id=f"chapter_{chapter_num:03d}",
                chapter_number=chapter_num,
                title=f"Chapter {chapter_num}",
                start_time=current_scenes[0].start_time,
                end_time=current_scenes[-1].end_time,
                scene_ids=[s.id for s in current_scenes],
            )
            chapters.append(chapter)

        return chapters
