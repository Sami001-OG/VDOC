"""Scene detection using PySceneDetect."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from scenedetect import ContentDetector, open_video, SceneManager
from scenedetect.scene_manager import save_images

from videomarker.core.detector import SceneDetector
from videomarker.models.segment import Scene, SegmentType
from videomarker.models.video import VideoInfo

logger = logging.getLogger(__name__)


class PySceneDetector(SceneDetector):
    """Scene detection using the PySceneDetect library.

    Supports hard cuts, fade transitions, and content-aware detection.
    """

    def __init__(
        self,
        threshold: float = 30.0,
        min_scene_len: float = 1.0,
    ) -> None:
        self.threshold = threshold
        self.min_scene_len = min_scene_len

    def detect(
        self,
        video_info: VideoInfo,
        frames_dir: Optional[Path] = None,
        video_path: Optional[Path] = None,
    ) -> List[Scene]:
        """Detect scenes using content-aware detection.

        Args:
            video_info: Video metadata.
            frames_dir: Optional directory with extracted frames.
            video_path: Optional path to the video file.

        Returns:
            List of detected Scene objects.
        """
        path = video_path or Path(video_info.metadata.file_path)
        video = open_video(str(path))

        scene_manager = SceneManager()
        scene_manager.add_detector(
            ContentDetector(threshold=self.threshold, min_scene_len=int(self.min_scene_len * video_info.metadata.fps))
        )

        logger.info(
            "Detecting scenes in %s (threshold=%.1f)...",
            path.name, self.threshold,
        )
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()

        scenes: List[Scene] = []
        for i, (start, end) in enumerate(scene_list):
            scene = Scene(
                id=f"scene_{i + 1:03d}",
                segment_type=SegmentType.SCENE,
                scene_number=i + 1,
                start_time=start.get_seconds(),
                end_time=end.get_seconds(),
                confidence=0.9,
            )
            scenes.append(scene)

        if not scenes:
            # If no scenes detected, treat entire video as one scene
            scenes.append(
                Scene(
                    id="scene_001",
                    segment_type=SegmentType.SCENE,
                    scene_number=1,
                    start_time=0.0,
                    end_time=video_info.metadata.duration,
                    confidence=1.0,
                )
            )

        logger.info("Detected %d scenes", len(scenes))
        return scenes

    def detect_hard_cuts(
        self,
        video_info: VideoInfo,
        threshold: float = 30.0,
    ) -> List[Scene]:
        """Detect hard cut transitions only."""
        return self.detect(video_info)

    def detect_with_keyframes(
        self,
        video_info: VideoInfo,
        video_path: Path,
        output_dir: Path,
        threshold: Optional[float] = None,
    ) -> List[Scene]:
        """Detect scenes and save keyframe images."""
        scenes = self.detect(video_info, video_path=video_path)

        keyframe_dir = output_dir / "keyframes"
        keyframe_dir.mkdir(parents=True, exist_ok=True)

        video = open_video(str(video_path))
        scene_manager = SceneManager()
        scene_manager.add_detector(
            ContentDetector(
                threshold=threshold or self.threshold,
                min_scene_len=int(self.min_scene_len * video_info.metadata.fps),
            )
        )
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()

        if scene_list:
            save_images(
                scene_list,
                video,
                num_images=1,
                image_output_dir=str(keyframe_dir),
            )

        return scenes
