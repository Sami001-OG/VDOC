"""PaddleOCR provider."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from videomarker.providers.base import ProviderConfig, ProviderStatus
from videomarker.providers.ocr.base import OCRProvider

logger = logging.getLogger(__name__)


class PaddleOCRProvider(OCRProvider):
    """OCR using PaddleOCR."""

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        super().__init__(config)
        self._ocr = None

    async def initialize(self) -> None:
        try:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                use_gpu=self.config.device == "cuda",
                show_log=False,
            )
            self.status = ProviderStatus.READY
        except ImportError:
            logger.warning("PaddleOCR not installed. Install: pip install paddleocr")
            raise

    async def extract_text(self, image_path: Path) -> Dict[str, Any]:
        if not self._ocr:
            raise RuntimeError("Provider not initialized")

        result = self._ocr.ocr(str(image_path), cls=True)

        blocks = []
        text_parts = []
        if result and result[0]:
            for line_info in result[0]:
                bbox, (text, confidence) = line_info
                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": [float(p) for point in bbox for p in point],
                })
                text_parts.append(text)

        return {
            "text": "\n".join(text_parts),
            "blocks": blocks,
            "language": "en",
        }

    async def extract_batch(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        results = []
        for path in image_paths:
            results.append(await self.extract_text(path))
        return results
