"""OpenCV-based frame extraction."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from tqdm import tqdm

from videomarker.core.extractor import FrameExtractor
from videomarker.models.video import VideoInfo

logger = logging.getLogger(__name__)


class OpenCVFrameExtractor(FrameExtractor):
    """Extract frames from video using OpenCV."""

    def __init__(
        self,
        fps: float = 1.0,
        max_frames: Optional[int] = None,
        quality: int = 95,
    ) -> None:
        self.fps = fps
        self.max_frames = max_frames
        self.quality = quality

    def extract(
        self,
        video_info: VideoInfo,
        output_dir: Path,
        fps: Optional[float] = None,
        max_frames: Optional[int] = None,
    ) -> List[Path]:
        """Extract frames at regular intervals."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cap = self._open_video(video_info)
        try:
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            target_fps = fps or self.fps
            frame_interval = max(1, int(video_fps / target_fps))
            max_f = max_frames or self.max_frames or total_frames

            extracted: List[Path] = []
            count = 0
            frame_idx = 0

            pbar = tqdm(total=min(total_frames, max_f * frame_interval), desc="Extracting frames")
            while count < max_f:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_interval == 0:
                    timestamp = frame_idx / video_fps
                    frame_path = output_dir / f"frame_{count:06d}_{timestamp:.3f}s.jpg"
                    cv2.imwrite(str(frame_path), frame, [
                        cv2.IMWRITE_JPEG_QUALITY, self.quality
                    ])
                    extracted.append(frame_path)
                    count += 1

                frame_idx += 1
                pbar.update(1)

            pbar.close()
            logger.info("Extracted %d frames to %s", len(extracted), output_dir)
            return extracted
        finally:
            cap.release()

    def extract_at_timestamps(
        self,
        video_info: VideoInfo,
        timestamps: List[float],
        output_dir: Path,
    ) -> List[Path]:
        """Extract frames at specific timestamps."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cap = self._open_video(video_info)
        try:
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            extracted: List[Path] = []

            for ts in timestamps:
                frame_idx = int(ts * video_fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frame_path = output_dir / f"frame_{ts:.3f}s.jpg"
                    cv2.imwrite(str(frame_path), frame, [
                        cv2.IMWRITE_JPEG_QUALITY, self.quality
                    ])
                    extracted.append(frame_path)

            logger.info("Extracted %d frames at specific timestamps", len(extracted))
            return extracted
        finally:
            cap.release()

    def extract_keyframe(
        self, video_path: Path, timestamp: float, output_path: Path
    ) -> Optional[Path]:
        """Extract a single keyframe at the given timestamp."""
        cap = cv2.VideoCapture(str(video_path))
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_idx = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(output_path), frame, [
                    cv2.IMWRITE_JPEG_QUALITY, self.quality
                ])
                return output_path
            return None
        finally:
            cap.release()

    def _open_video(self, video_info: VideoInfo) -> cv2.VideoCapture:
        """Open the video file with OpenCV."""
        path = str(video_info.metadata.file_path)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {path}")
        return cap
