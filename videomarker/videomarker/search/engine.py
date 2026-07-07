"""Search engine — semantic search across transcript, OCR, captions, summaries, and concepts."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class SearchEngine:
    """Semantic search over all video analysis data.

    Searches across: transcript, OCR, captions, summaries, concepts.
    """

    def __init__(self) -> None:
        self._index: Optional[Any] = None
        self._documents: List[Dict[str, Any]] = []

    def build_index(self, documents: List[Dict[str, Any]]) -> None:
        """Build FAISS index from documents with embeddings.

        Each document should have: id, text, vector, source_type, timestamp.
        """
        self._documents = documents
        vectors = np.array([d["vector"] for d in documents if d.get("vector")], dtype=np.float32)

        if len(vectors) == 0:
            logger.warning("No vectors to index")
            return

        try:
            import faiss
            dimension = vectors.shape[1]
            self._index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(vectors)
            self._index.add(vectors)
            logger.info("Search index built: %d documents, %d dims", len(documents), dimension)
        except ImportError:
            logger.warning("FAISS not installed, using brute force")
            self._index = None

    def search(self, query: str, top_k: int = 10, embed_fn=None) -> List[Dict[str, Any]]:
        """Search for content semantically similar to the query.

        Args:
            query: Natural language query.
            top_k: Number of results to return.
            embed_fn: Function to embed the query text. If None, returns text matches.

        Returns:
            List of result dicts with id, text, score, source_type, timestamp.
        """
        if not embed_fn:
            return self._text_search(query, top_k)

        query_vec = embed_fn(query)
        query_arr = np.array([query_vec], dtype=np.float32)

        if self._index is not None:
            import faiss
            faiss.normalize_L2(query_arr)
            scores, indices = self._index.search(query_arr, top_k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if 0 <= idx < len(self._documents):
                    doc = self._documents[idx]
                    results.append({
                        "id": doc["id"],
                        "text": doc["text"][:300],
                        "score": float(score),
                        "source_type": doc.get("source_type", ""),
                        "timestamp": doc.get("timestamp", 0),
                    })
            return results

        return self._brute_force(query_vec, top_k)

    def _text_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword/text search fallback."""
        query_lower = query.lower()
        scored = []
        for doc in self._documents:
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

    def _brute_force(self, query_vec: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Brute force cosine similarity."""
        query_np = np.array(query_vec)
        query_norm = np.linalg.norm(query_np)
        scored = []
        for doc in self._documents:
            vec = np.array(doc.get("vector", []))
            if len(vec) == 0:
                continue
            vec_norm = np.linalg.norm(vec)
            if query_norm > 0 and vec_norm > 0:
                sim = float(np.dot(query_np, vec) / (query_norm * vec_norm))
            else:
                sim = 0
            scored.append((sim, doc))

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

    def load(self, path: str) -> None:
        """Load index from disk."""
        with open(path) as f:
            data = json.load(f)
        self._documents = data.get("documents", [])
        vectors = np.array([d["vector"] for d in self._documents if d.get("vector")], dtype=np.float32)

        if len(vectors) > 0:
            try:
                import faiss
                self._index = faiss.IndexFlatIP(vectors.shape[1])
                faiss.normalize_L2(vectors)
                self._index.add(vectors)
            except ImportError:
                self._index = None

    def save(self, path: str) -> None:
        """Save index to disk."""
        data = {
            "documents": [
                {k: v for k, v in d.items() if k != "vector" or isinstance(v, list)}
                for d in self._documents
            ]
        }
        Path(path).write_text(json.dumps(data, indent=2))

    def add_document(self, doc: Dict[str, Any]) -> None:
        """Add a single document to the index."""
        self._documents.append(doc)
