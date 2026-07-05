"""OCR processor — extracts text from keyframes using OCR engines."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from videomarker.core.processor import Processor
from videomarker.core.plugin import processor
from videomarker.models.ocr import OCRBlock, OCRLine, OCRResult, OCRWord

logger = logging.getLogger(__name__)


@processor("ocr", dependencies=["scene_detect"], priority=20)
class OCRProcessor(Processor):
    """Extract text from keyframes and scene images."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ocr_engine = None

    def process(self, context: Any) -> None:
        """Run OCR on scene keyframes."""
        scenes = context.data.get("scenes", [])
        timeline = context.data.get("timeline")
        if not scenes and not timeline:
            logger.warning("No scenes detected, skipping OCR")
            return

        ocr_results: Dict[str, OCRResult] = {}
        video_path = Path(context.data["video_path"])

        for scene in scenes:
            keyframe_path = self._get_keyframe(scene, video_path)
            if keyframe_path and keyframe_path.exists():
                result = self._run_ocr(keyframe_path, scene.start_time)
                ocr_results[scene.id] = result

                # Save OCR text for this scene
                scene.ocr_path = keyframe_path.parent / f"{scene.id}_ocr.md"
                scene.ocr_path.parent.mkdir(parents=True, exist_ok=True)
                scene.ocr_path.write_text(result.full_text, encoding="utf-8")

        context.data["ocr_results"] = ocr_results
        logger.info("OCR complete: %d scenes processed", len(ocr_results))

    def _get_keyframe(self, scene: Any, video_path: Path) -> Optional[Path]:
        """Get or extract a keyframe image for the scene."""
        if scene.keyframe_path and Path(scene.keyframe_path).exists():
            return Path(scene.keyframe_path)

        # Try to extract keyframe at the middle of the scene
        midpoint = (scene.start_time + scene.end_time) / 2
        keyframe_dir = Path(video_path).parent / f"{Path(video_path).stem}.markdir" / "scenes" / scene.id
        keyframe_dir.mkdir(parents=True, exist_ok=True)
        keyframe_path = keyframe_dir / "keyframe.jpg"

        try:
            from videomarker.extractors.frame import OpenCVFrameExtractor
            extractor = OpenCVFrameExtractor()
            return extractor.extract_keyframe(
                video_path=Path(video_path),
                timestamp=midpoint,
                output_path=keyframe_path,
            )
        except Exception as e:
            logger.warning("Failed to extract keyframe for %s: %s", scene.id, e)
            return None

    def _run_ocr(self, image_path: Path, timestamp: float) -> OCRResult:
        """Run OCR on the given image."""
        engine = self.settings.ocr_engine if self.settings else "paddle"

        try:
            if engine == "paddle":
                return self._paddle_ocr(image_path, timestamp)
            elif engine == "surya":
                return self._surya_ocr(image_path, timestamp)
            else:
                return self._tesseract_fallback(image_path, timestamp)
        except Exception as e:
            logger.warning("OCR failed for %s: %s", image_path, e)
            return OCRResult(blocks=[], text="", image_path=str(image_path), timestamp=timestamp)

    def _paddle_ocr(self, image_path: Path, timestamp: float) -> OCRResult:
        """Run OCR with PaddleOCR."""
        try:
            from paddleocr import PaddleOCR

            ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                use_gpu=self.settings.gpu_enabled if self.settings else False,
                show_log=False,
            )
            result = ocr.ocr(str(image_path), cls=True)
        except ImportError:
            logger.warning("PaddleOCR not installed. Try: pip install paddleocr")
            return self._tesseract_fallback(image_path, timestamp)

        blocks: List[OCRBlock] = []
        full_texts: List[str] = []

        if result and result[0]:
            for line_info in result[0]:
                bbox, (text, confidence) = line_info
                x0 = min(p[0] for p in bbox)
                y0 = min(p[1] for p in bbox)
                x1 = max(p[0] for p in bbox)
                y1 = max(p[1] for p in bbox)

                word = OCRWord(
                    text=text,
                    confidence=confidence,
                    x0=x0, y0=y0, x1=x1, y1=y1,
                )
                line = OCRLine(
                    text=text,
                    words=[word],
                    confidence=confidence,
                    x0=x0, y0=y0, x1=x1, y1=y1,
                )
                block = OCRBlock(
                    text=text,
                    lines=[line],
                    block_type="text",
                    confidence=confidence,
                    x0=x0, y0=y0, x1=x1, y1=y1,
                )
                blocks.append(block)
                full_texts.append(text)

        return OCRResult(
            blocks=blocks,
            text="\n".join(full_texts) if full_texts else "",
            image_path=str(image_path),
            timestamp=timestamp,
        )

    def _surya_ocr(self, image_path: Path, timestamp: float) -> OCRResult:
        """Run OCR with Surya OCR."""
        try:
            from surya.ocr import run_ocr
            from surya.model.recognition.model import load_model as load_recognition
            from surya.model.recognition.processor import load_processor as load_rec_processor
            from surya.model.detection.model import load_model as load_detection
            from surya.model.detection.processor import load_processor as load_det_processor

            from PIL import Image

            langs = self.settings.ocr_languages if self.settings else ["en"]
            det_model = load_detection()
            det_processor = load_det_processor()
            rec_model = load_recognition()
            rec_processor = load_rec_processor()

            image = Image.open(str(image_path))
            predictions = run_ocr(
                [image], [langs], det_model, det_processor, rec_model, rec_processor
            )

            blocks: List[OCRBlock] = []
            full_texts: List[str] = []
            if predictions and predictions[0]:
                for pred in predictions[0].text_lines:
                    block = OCRBlock(
                        text=pred.text,
                        block_type="text",
                        confidence=pred.confidence,
                        x0=pred.bbox[0], y0=pred.bbox[1],
                        x1=pred.bbox[2], y1=pred.bbox[3],
                    )
                    blocks.append(block)
                    full_texts.append(pred.text)

            return OCRResult(
                blocks=blocks,
                text="\n".join(full_texts),
                image_path=str(image_path),
                timestamp=timestamp,
            )
        except ImportError:
            logger.warning("Surya OCR not installed. Try: pip install surya-ocr")
            return self._tesseract_fallback(image_path, timestamp)

    def _tesseract_fallback(self, image_path: Path, timestamp: float) -> OCRResult:
        """Fallback to pytesseract if available."""
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(str(image_path))
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            blocks: List[OCRBlock] = []
            current_text: List[str] = []

            for i in range(len(data["text"])):
                if data["text"][i].strip():
                    current_text.append(data["text"][i])

            text = " ".join(current_text)
            return OCRResult(
                blocks=[OCRBlock(text=text, block_type="text", confidence=0.5, x0=0, y0=0, x1=0, y1=0)],
                text=text,
                image_path=str(image_path),
                timestamp=timestamp,
            )
        except ImportError:
            logger.warning("No OCR engine available. Install PaddleOCR: pip install paddleocr")
            return OCRResult(blocks=[], text="", image_path=str(image_path), timestamp=timestamp)
