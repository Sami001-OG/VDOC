"""Search index stage — builds the FAISS search index from embeddings."""

from __future__ import annotations

import logging
from pathlib import Path

from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.search.engine import SearchEngine

logger = logging.getLogger(__name__)


class SearchIndexStage(PipelineStage):
    """Build a search index from generated embeddings for semantic search."""

    stage_name = "search_index"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not ctx.embeddings:
            logger.warning("No embeddings to index")
            return ctx

        engine = SearchEngine()
        if ctx.embeddings and hasattr(ctx.embeddings[0], "__dataclass_fields__"):
            index_data = [
                {"id": e.id, "vector": e.vector, "text": e.text,
                 "source_type": e.source_type, "timestamp": e.timestamp}
                for e in ctx.embeddings
            ]
        else:
            index_data = ctx.embeddings  # type: ignore
        engine.build_index(index_data)

        index_path = Path(ctx.output_dir) / "search.index"
        engine.save(str(index_path))

        ctx.search_index = {
            "path": str(index_path),
            "num_documents": len(ctx.embeddings),
        }

        logger.info("Search index saved: %d documents at %s", len(ctx.embeddings), index_path)
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return bool(ctx.embeddings)
