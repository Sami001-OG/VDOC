"""Search engine — semantic search across transcript, OCR, captions, summaries, and concepts."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from vdoc.providers.search import FAISSSearchProvider, SearchProvider

logger = logging.getLogger(__name__)


class SearchEngine:
    """Semantic search over all video analysis data.

    Uses SearchProvider for vector operations.
    """

    def __init__(self, search_provider: Optional[SearchProvider] = None) -> None:
        self._provider = search_provider or FAISSSearchProvider()

    def build_index(self, documents: List[Dict[str, Any]]) -> None:
        """Build search index from documents with embeddings."""
        vectors = [d["vector"] for d in documents if d.get("vector")]
        self._provider.build_index(vectors, documents)
        logger.info("Search index built: %d documents", len(documents))

    def search(self, query: str, top_k: int = 10, embed_fn: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Search for content semantically similar to the query."""
        if not embed_fn:
            return self._text_search(query, top_k)

        query_vec = embed_fn(query)
        return self._provider.search(query_vec, top_k)

    def _text_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword/text search fallback."""
        query_lower = query.lower()
        scored = []
        for doc in self._provider._documents if hasattr(self._provider, '_documents') else []:
            text = doc.get("text", "").lower()
            score = text.count(query_lower) / max(len(text.split()), 1)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": d["id"],
                "text": d["text"][:300],
                "score": s,
                "source_type": d.get("source_type", ""),
                "timestamp": d.get("timestamp", 0),
            }
            for s, d in scored[:top_k]
        ]

    def add_document(self, doc: Dict[str, Any]) -> None:
        """Add a single document to the index."""
        vector = doc.get("vector", [])
        self._provider.add(vector, doc)

    def load(self, path: str) -> None:
        self._provider.load(path)

    def save(self, path: str) -> None:
        self._provider.save(path)
