"""Embedding stage — generates vector embeddings from transcript and scenes."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from vdoc.models.document import Embedding
from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class EmbeddingStage(PipelineStage):
    """Generate embeddings for transcript segments, scene descriptions, and OCR text."""

    stage_name = "embedding"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        provider = await ProviderRegistry.get("embedding")
        if not provider:
            logger.warning("No embedding provider registered, skipping")
            return ctx

        texts_to_embed: List[Dict[str, str]] = []
        meta: List[Dict] = []

        if ctx.transcript:
            for seg in ctx.transcript.segments:
                text = seg.text.strip()
                if text:
                    texts_to_embed.append({"text": text})
                    meta.append({"source_type": "transcript", "timestamp": seg.start, "scene_id": self._find_scene(ctx, seg.start)})

        for scene in ctx.scenes:
            desc = (scene.description or "").strip()
            if desc:
                texts_to_embed.append({"text": desc})
                meta.append({"source_type": "scene_description", "timestamp": scene.start_time, "scene_id": scene.id})

        for scene_id, ocr_data in ctx.ocr_results.items():
            text = ocr_data.text.strip()
            if text:
                texts_to_embed.append({"text": text})
                meta.append({"source_type": "ocr", "timestamp": 0, "scene_id": scene_id})

        if not texts_to_embed:
            logger.info("No texts to embed")
            return ctx

        texts = [d["text"] for d in texts_to_embed]
        vectors = await provider.embed(texts)

        embeddings = [
            Embedding(
                id=f"emb_{i+1:04d}",
                vector=vec,
                text=texts_to_embed[i]["text"],
                source_type=meta[i]["source_type"],
                timestamp=meta[i]["timestamp"],
            )
            for i, vec in enumerate(vectors)
        ]

        ctx.embeddings = embeddings
        logger.info("Embedding stage complete: %d vectors", len(embeddings))
        return ctx

    def _find_scene(self, ctx: PipelineContext, timestamp: float) -> str:
        for scene in ctx.scenes:
            if scene.start_time <= timestamp <= scene.end_time:
                return scene.id
        return ""

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("embedding_provider", "sentence") != "none"
