from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from vdoc.providers.search.base import SearchProvider

logger = logging.getLogger(__name__)


class FAISSSearchProvider(SearchProvider):
    """Vector search using FAISS index."""

    def __init__(self) -> None:
        self._index: Optional[Any] = None
        self._documents: List[Dict[str, Any]] = []

    def build_index(self, vectors: List[List[float]], documents: List[Dict[str, Any]]) -> None:
        self._documents = documents
        if not vectors:
            logger.warning("No vectors to index")
            return

        vec_array = np.array(vectors, dtype=np.float32)
        dimension = vec_array.shape[1]

        try:
            import faiss
            self._index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(vec_array)
            self._index.add(vec_array)
            logger.info("Index built: %d vectors, %d dims", len(vectors), dimension)
        except ImportError:
            logger.warning("FAISS not installed, using brute force")
            self._index = None

    def search(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        if not self._documents:
            return []

        query_arr = np.array([query_vector], dtype=np.float32)

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
                        "text": doc.get("text", "")[:300],
                        "score": float(score),
                        "source_type": doc.get("source_type", ""),
                        "timestamp": doc.get("timestamp", 0),
                    })
            return results

        return self._brute_force(query_arr[0], top_k)

    def add(self, vector: List[float], document: Dict[str, Any]) -> None:
        self._documents.append(document)
        if self._index is not None:
            vec = np.array([vector], dtype=np.float32)
            import faiss
            faiss.normalize_L2(vec)
            self._index.add(vec)

    def save(self, path: str) -> None:
        data = {
            "documents": [
                {k: v for k, v in d.items() if k != "vector" or isinstance(v, list)}
                for d in self._documents
            ]
        }
        Path(path).write_text(json.dumps(data, indent=2))

    def load(self, path: str) -> None:
        with open(path) as f:
            data = json.load(f)
        self._documents = data.get("documents", [])
        vectors = [d["vector"] for d in self._documents if d.get("vector")]
        self.build_index(vectors, self._documents)

    @property
    def size(self) -> int:
        return len(self._documents)

    def _brute_force(self, query_vec: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        query_norm = np.linalg.norm(query_vec)
        scored = []
        for doc in self._documents:
            vec = np.array(doc.get("vector", []))
            if len(vec) == 0:
                continue
            vec_norm = np.linalg.norm(vec)
            sim = float(np.dot(query_vec, vec) / (query_norm * vec_norm)) if query_norm > 0 and vec_norm > 0 else 0
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
