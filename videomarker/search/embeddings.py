"""Embedding generation and semantic search engine."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from videomarker.models.search import Embedding, SearchIndex, SearchResult

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate vector embeddings for text content."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        device: str = "cpu",
    ) -> None:
        self.model_name = model_name
        self.device = device
        self._model = None
        self._dimension = 1024

    def generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            return self._generate_with_sentence_transformers(texts)
        except ImportError:
            try:
                return self._generate_with_openai(texts)
            except Exception as e:
                logger.warning("Embedding generation failed: %s", e)
                return self._generate_random(texts)

    def _generate_with_sentence_transformers(
        self, texts: List[str]
    ) -> List[List[float]]:
        """Generate embeddings using sentence-transformers."""
        from sentence_transformers import SentenceTransformer

        if self._model is None:
            self._model = SentenceTransformer(
                self.model_name, device=self.device
            )
            self._dimension = self._model.get_sentence_embedding_dimension()

        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def _generate_with_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using an OpenAI-compatible API."""
        from openai import OpenAI

        client = OpenAI()
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=texts,
        )
        return [d.embedding for d in response.data]

    def _generate_random(self, texts: List[str]) -> List[List[float]]:
        """Fallback: generate random embeddings (for testing)."""
        rng = np.random.default_rng(42)
        return rng.random((len(texts), self._dimension)).tolist()


class SearchEngine:
    """Semantic search over video content using vector embeddings."""

    def __init__(self, index_type: str = "flat") -> None:
        self.index_type = index_type
        self._index = None
        self._embeddings: List[Embedding] = []
        self._generator: Optional[EmbeddingGenerator] = None

    def build_index(
        self,
        embeddings: List[Embedding],
        generator: Optional[EmbeddingGenerator] = None,
    ) -> SearchIndex:
        """Build a search index from embeddings."""
        self._embeddings = embeddings
        self._generator = generator

        if not embeddings:
            return SearchIndex()

        vectors = np.array([e.vector for e in embeddings], dtype=np.float32)

        try:
            import faiss
            dimension = vectors.shape[1]
            if self.index_type == "flat":
                self._index = faiss.IndexFlatIP(dimension)
            else:
                self._index = faiss.IndexFlatIP(dimension)

            faiss.normalize_L2(vectors)
            self._index.add(vectors)
        except ImportError:
            logger.warning("FAISS not installed, using brute force search")
            self._index = None

        return SearchIndex(
            model_name=generator.model_name if generator else "unknown",
            dimension=vectors.shape[1],
            num_embeddings=len(embeddings),
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        generator: Optional[EmbeddingGenerator] = None,
    ) -> List[SearchResult]:
        """Search for content similar to the query."""
        gen = generator or self._generator
        if not gen:
            raise ValueError("No embedding generator provided")

        query_vector = gen.generate([query])[0]
        query_array = np.array([query_vector], dtype=np.float32)

        if self._index is not None:
            import faiss
            faiss.normalize_L2(query_array)
            scores, indices = self._index.search(query_array, top_k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self._embeddings):
                    emb = self._embeddings[idx]
                    results.append(
                        SearchResult(
                            id=emb.id,
                            text=emb.text,
                            score=float(score),
                            source_type=emb.source_type,
                            timestamp=emb.timestamp,
                        )
                    )
            return results
        else:
            return self._brute_force_search(query_array[0], top_k)

    def _brute_force_search(
        self, query_vector: List[float], top_k: int
    ) -> List[SearchResult]:
        """Fallback brute force cosine similarity search."""
        scores = []
        query_np = np.array(query_vector)
        query_norm = np.linalg.norm(query_np)

        for emb in self._embeddings:
            emb_np = np.array(emb.vector)
            emb_norm = np.linalg.norm(emb_np)
            if query_norm > 0 and emb_norm > 0:
                similarity = np.dot(query_np, emb_np) / (query_norm * emb_norm)
            else:
                similarity = 0
            scores.append((similarity, emb))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, emb in scores[:top_k]:
            results.append(
                SearchResult(
                    id=emb.id,
                    text=emb.text,
                    score=float(score),
                    source_type=emb.source_type,
                    timestamp=emb.timestamp,
                )
            )
        return results

    def save(self, path: Path) -> None:
        """Save the search index and embeddings to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "embeddings": [
                {
                    "id": e.id,
                    "vector": e.vector,
                    "text": e.text,
                    "source_type": e.source_type,
                    "timestamp": e.timestamp,
                    "metadata": e.metadata,
                }
                for e in self._embeddings
            ],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("Search index saved to %s (%d embeddings)", path, len(self._embeddings))

    def load(self, path: Path) -> SearchIndex:
        """Load a search index from disk."""
        data = json.loads(path.read_text(encoding="utf-8"))
        self._embeddings = [Embedding(**e) for e in data["embeddings"]]
        vectors = np.array([e.vector for e in self._embeddings], dtype=np.float32)

        try:
            import faiss
            dimension = vectors.shape[1]
            self._index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(vectors)
            self._index.add(vectors)
        except ImportError:
            self._index = None

        return SearchIndex(num_embeddings=len(self._embeddings))
