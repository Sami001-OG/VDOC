"""Vision understanding processor — describes scenes visually."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Optional

from videomarker.core.processor import Processor
from videomarker.core.plugin import processor
from videomarker.models.vision import (
    ObjectDetected,
    SceneDescription,
    VisionUnderstanding,
)

logger = logging.getLogger(__name__)


@processor("vision", dependencies=["scene_detect"], priority=30)
class VisionProcessor(Processor):
    """Generates visual descriptions of scenes using vision-language models."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._model = None

    def process(self, context: Any) -> None:
        """Generate visual understanding for each scene."""
        scenes = context.data.get("scenes", [])
        if not scenes:
            logger.warning("No scenes to analyze visually")
            return

        vision_results: dict = {}
        for scene in scenes:
            keyframe_path = self._find_keyframe(scene, context)
            if keyframe_path and keyframe_path.exists():
                understanding = self._analyze_scene(keyframe_path, scene.start_time)
                vision_results[scene.id] = understanding
                scene.description = understanding.description.summary
            else:
                understanding = VisionUnderstanding(
                    description=SceneDescription(
                        summary=f"Scene {scene.scene_number}",
                        detailed="No keyframe available for analysis.",
                    ),
                    timestamp=scene.start_time,
                )
                vision_results[scene.id] = understanding

        context.data["vision_results"] = vision_results
        logger.info("Vision analysis complete: %d scenes", len(vision_results))

    def _find_keyframe(self, scene: Any, context: Any) -> Optional[Path]:
        """Find the keyframe for a scene."""
        if scene.keyframe_path:
            return Path(scene.keyframe_path)

        scene_dir = Path(context.data.get("frames_dir", "")) / scene.id
        if scene_dir.exists():
            jpgs = list(scene_dir.glob("*.jpg"))
            if jpgs:
                return jpgs[0]

        return None

    def _analyze_scene(self, image_path: Path, timestamp: float) -> VisionUnderstanding:
        """Analyze a scene using available vision models."""
        try:
            return self._analyze_with_llm(image_path, timestamp)
        except Exception as e:
            logger.warning("LLM vision analysis failed: %s", e)
            return VisionUnderstanding(
                description=SceneDescription(
                    summary=f"Visual content at {timestamp:.1f}s",
                    detailed=f"Scene at timestamp {timestamp:.1f} seconds.",
                ),
                timestamp=timestamp,
                image_path=str(image_path),
            )

    def _analyze_with_llm(
        self, image_path: Path, timestamp: float
    ) -> VisionUnderstanding:
        """Use an OpenAI-compatible vision API to analyze the scene."""
        import base64

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        prompt = self.settings.scene_description_prompt if self.settings else (
            "Describe this video scene in detail. What is happening? "
            "What objects, people, UI elements, diagrams, or text are visible? "
            "Is this a slide presentation, code editor, terminal, diagram, or live demo?"
        )

        try:
            from openai import OpenAI
            client_kwargs = {}
            if self.settings:
                client_kwargs["base_url"] = self.settings.base_url
                if self.settings.api_key:
                    client_kwargs["api_key"] = self.settings.api_key

            client = OpenAI(**client_kwargs)
            model = self.settings.vision_model if self.settings else "gpt-4o"

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
                temperature=0.1,
            )

            description_text = response.choices[0].message.content or ""

            # Parse description into structured fields
            scene_desc = SceneDescription(
                summary=description_text[:200],
                detailed=description_text,
                tags=self._extract_tags(description_text),
            )

            return VisionUnderstanding(
                description=scene_desc,
                timestamp=timestamp,
                image_path=str(image_path),
            )

        except Exception as e:
            logger.error("LLM vision API error: %s", e)
            raise

    def _extract_tags(self, text: str) -> List[str]:
        """Extract simple tags from description text."""
        tags = []
        keywords = [
            "slide", "code", "terminal", "diagram", "chart", "graph",
            "presentation", "whiteboard", "browser", "editor", "IDE",
            "person", "screen", "document", "book", "equation",
        ]
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                tags.append(kw)
        return tags
