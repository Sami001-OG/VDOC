"""Embedding stage — generates vector embeddings from transcript and scenes."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

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

        texts_to_embed: List[Dict[str, Any]] = []

        for seg in ctx.transcript.get("segments", []):
            text = seg.get("text", "").strip()
            if text:
                texts_to_embed.append({
                    "text": text,
                    "source_type": "transcript",
                    "timestamp": seg.get("start", 0),
                    "scene_id": self._find_scene(ctx, seg.get("start", 0)),
                })

        for scene in ctx.scenes:
            desc = scene.get("description", "").strip()
            if desc:
                texts_to_embed.append({
                    "text": desc,
                    "source_type": "scene_description",
                    "timestamp": scene.get("start_time", 0),
                    "scene_id": scene.get("id"),
                })

        for scene_id, ocr_data in (ctx.ocr_results or {}).items():
            text = (ocr_data.get("text", "") if isinstance(ocr_data, dict) else "").strip()
            if text:
                texts_to_embed.append({
                    "text": text,
                    "source_type": "ocr",
                    "timestamp": 0,
                    "scene_id": scene_id,
                })

        if not texts_to_embed:
            logger.info("No texts to embed")
            return ctx

        texts = [d["text"] for d in texts_to_embed]
        vectors = await provider.embed(texts)

        embeddings = []
        for i, vec in enumerate(vectors):
            embeddings.append({
                "id": f"emb_{i+1:04d}",
                "vector": vec,
                "text": texts_to_embed[i]["text"],
                "source_type": texts_to_embed[i]["source_type"],
                "timestamp": texts_to_embed[i]["timestamp"],
                "scene_id": texts_to_embed[i]["scene_id"],
            })

        ctx.embeddings = embeddings
        logger.info("Embedding stage complete: %d vectors", len(embeddings))
        return ctx

    def _find_scene(self, ctx: PipelineContext, timestamp: float) -> str:
        for scene in ctx.scenes:
            if scene.get("start_time", 0) <= timestamp <= scene.get("end_time", 0):
                return scene.get("id", "")
        return ""

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("embedding_provider", "sentence") != "none"
