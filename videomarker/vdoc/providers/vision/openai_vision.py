"""Vision provider using OpenAI-compatible vision API."""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from vdoc.providers.base import ProviderConfig, ProviderStatus
from vdoc.providers.vision.base import VisionProvider

logger = logging.getLogger(__name__)


class OpenAIVisionProvider(VisionProvider):
    """Vision understanding via OpenAI-compatible vision endpoints."""

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        super().__init__(config)
        self._client: Optional[AsyncOpenAI] = None

    async def initialize(self) -> None:
        self._client = AsyncOpenAI(
            base_url=self.config.extra.get("base_url", "https://api.openai.com/v1"),
            api_key=self.config.extra.get("api_key", ""),
        )
        self.status = ProviderStatus.READY

    async def describe(
        self, image_path: Path, prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("Provider not initialized")

        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt_text = prompt or "Describe this image in detail. What objects, people, text, UI elements, or diagrams are visible?"

        response = await self._client.chat.completions.create(
            model=self.config.model or "gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}},
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.1,
        )

        text = response.choices[0].message.content or ""
        return {
            "summary": text[:200],
            "detailed": text,
            "tags": self._extract_tags(text),
            "objects": [],
            "activities": [],
        }

    async def analyze_batch(
        self, image_paths: List[Path], prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for path in image_paths:
            results.append(await self.describe(path, prompt))
        return results

    def _extract_tags(self, text: str) -> List[str]:
        tags = []
        keywords = ["slide", "code", "terminal", "diagram", "chart", "person", "screen", "whiteboard", "browser", "editor"]
        for kw in keywords:
            if kw in text.lower():
                tags.append(kw)
        return tags

    async def close(self) -> None:
        await self._client.close() if self._client else None
        self.status = ProviderStatus.CLOSED
