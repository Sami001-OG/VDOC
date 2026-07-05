"""Pipeline orchestration — coordinates the full video processing workflow."""

from __future__ import annotations

import logging
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from videomarker.config.settings import VideoMarkerSettings
from videomarker.core.plugin import PluginRegistry, ProcessorPlugin
from videomarker.models.video import VideoInfo
from videomarker.models.markdirectory import Manifest

logger = logging.getLogger(__name__)


class PipelineStep(str, Enum):
    """Defines the ordered stages of the pipeline."""

    PROVIDER = "provider"
    FRAME_EXTRACT = "frame_extract"
    AUDIO_EXTRACT = "audio_extract"
    SCENE_DETECT = "scene_detect"
    TIMELINE_BUILD = "timeline_build"
    PROCESSORS = "processors"
    RENDER = "render"
    COMPLETE = "complete"


class PipelineContext(BaseModel):
    """Shared context passed through the pipeline stages.

    Every stage reads from and writes to this context, allowing
    independent, decoupled pipeline steps.
    """

    video_info: Optional[VideoInfo] = None
    settings: Optional[VideoMarkerSettings] = None
    output_dir: Optional[Path] = None
    manifest: Optional[Manifest] = None
    status: Dict[str, str] = Field(default_factory=dict)
    errors: Dict[str, str] = Field(default_factory=dict)
    start_time: float = Field(default_factory=time.time)
    data: Dict[str, Any] = Field(default_factory=dict)
    cancelled: bool = False

    model_config = {"arbitrary_types_allowed": True}

    def update_status(self, step: str, status: str) -> None:
        self.status[step] = status
        logger.info("Pipeline [%s]: %s", step, status)

    def record_error(self, step: str, error: str) -> None:
        self.errors[step] = error
        logger.error("Pipeline [%s] error: %s", step, error)


class Pipeline:
    """Orchestrates the entire video processing pipeline.

    The pipeline is composed of independent stages. Each stage
    can be overridden or extended. Processors are discovered
    via the plugin system and run in dependency order.
    """

    def __init__(
        self,
        settings: Optional[VideoMarkerSettings] = None,
        plugins: Optional[List[str]] = None,
    ) -> None:
        self.settings = settings or VideoMarkerSettings()
        self.context = PipelineContext(settings=self.settings)
        self._steps: Dict[PipelineStep, Callable] = {}
        self._hooks: Dict[str, List[Callable]] = {
            "before_step": [],
            "after_step": [],
            "on_error": [],
            "on_complete": [],
        }

        self._register_default_steps()

    def _register_default_steps(self) -> None:
        """Register the default pipeline steps."""
        self.register_step(PipelineStep.PROVIDER, self._step_provider)
        self.register_step(PipelineStep.FRAME_EXTRACT, self._step_frame_extract)
        self.register_step(PipelineStep.AUDIO_EXTRACT, self._step_audio_extract)
        self.register_step(PipelineStep.SCENE_DETECT, self._step_scene_detect)
        self.register_step(PipelineStep.TIMELINE_BUILD, self._step_timeline_build)
        self.register_step(PipelineStep.PROCESSORS, self._step_processors)
        self.register_step(PipelineStep.RENDER, self._step_render)

    def register_step(self, step: PipelineStep, handler: Callable) -> None:
        """Register or override a pipeline step handler."""
        self._steps[step] = handler

    def add_hook(self, hook: str, callback: Callable) -> None:
        """Add a lifecycle hook callback."""
        if hook in self._hooks:
            self._hooks[hook].append(callback)

    def run(self, video_path: Path, output_dir: Optional[Path] = None) -> PipelineContext:
        """Execute the full pipeline on the given video."""
        self.context = PipelineContext(settings=self.settings)
        if output_dir:
            self.context.output_dir = output_dir

        self.context.data["video_path"] = video_path

        ordered_steps = list(PipelineStep)
        for step in ordered_steps:
            if self.context.cancelled:
                logger.warning("Pipeline cancelled at step %s", step.value)
                break

            if step not in self._steps:
                continue

            if step == PipelineStep.COMPLETE:
                continue

            self._run_hook("before_step", step)

            try:
                self.context.update_status(step.value, "running")
                self._steps[step]()
                self.context.update_status(step.value, "completed")
            except Exception as e:
                self.context.record_error(step.value, str(e))
                self._run_hook("on_error", step, e)
                raise

            self._run_hook("after_step", step)

        self.context.update_status(PipelineStep.COMPLETE.value, "completed")
        self._run_hook("on_complete")

        return self.context

    def _run_hook(self, hook: str, *args: Any, **kwargs: Any) -> None:
        for callback in self._hooks.get(hook, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.warning("Hook %s callback failed: %s", hook, e)

    def _step_provider(self) -> None:
        from videomarker.providers.ffmpeg import FFmpegVideoProvider
        video_path: Path = self.context.data["video_path"]
        provider = FFmpegVideoProvider()
        video_info = provider.load(video_path)
        self.context.video_info = video_info
        self.context.data["video_info"] = video_info

    def _step_frame_extract(self) -> None:
        from videomarker.extractors.frame import OpenCVFrameExtractor
        extractor = OpenCVFrameExtractor(
            fps=self.settings.frame_extraction_fps,
            max_frames=self.settings.max_frames,
        )
        video_path: Path = self.context.data["video_path"]
        frames_dir = (self.context.output_dir or video_path.parent) / "frames"
        extractor.extract(self.context.video_info, frames_dir)
        self.context.data["frames_dir"] = frames_dir

    def _step_audio_extract(self) -> None:
        from videomarker.extractors.audio import FFmpegAudioExtractor
        extractor = FFmpegAudioExtractor()
        video_path: Path = self.context.data["video_path"]
        audio_path = (self.context.output_dir or video_path.parent) / "audio.wav"
        extractor.extract(self.context.video_info, audio_path)
        self.context.data["audio_path"] = audio_path

    def _step_scene_detect(self) -> None:
        from videomarker.detectors.scene import PySceneDetector
        detector = PySceneDetector(
            threshold=self.settings.scene_detect_threshold,
        )
        scenes = detector.detect(self.context.data.get("frames_dir"), self.context.video_info)
        self.context.data["scenes"] = scenes

    def _step_timeline_build(self) -> None:
        from videomarker.core.builder import TimelineBuilder
        builder = TimelineBuilder()
        timeline = builder.build(
            scenes=self.context.data.get("scenes", []),
            video_info=self.context.video_info,
        )
        self.context.data["timeline"] = timeline

    def _step_processors(self) -> None:
        PluginRegistry.discover()
        plugins = PluginRegistry.get_all_plugins()
        selected = self.settings.enabled_processors
        for plugin in plugins:
            if selected and plugin.name not in selected:
                continue
            logger.info("Running processor: %s", plugin.name)
            processor = plugin.instantiate(settings=self.settings)
            processor.process(self.context)

    def _step_render(self) -> None:
        from videomarker.renderers.markdirectory import MarkDirectoryRenderer
        renderer = MarkDirectoryRenderer(self.settings)
        renderer.render(self.context)
