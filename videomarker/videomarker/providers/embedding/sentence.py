"""Sentence-transformers embedding provider."""

from __future__ import annotations

import logging
from typing import List, Optional

from videomarker.providers.base import ProviderConfig, ProviderStatus
from videomarker.providers.embedding.base import EmbeddingProvider

logger = logging.getLogger(__name__)


class SentenceEmbeddingProvider(EmbeddingProvider):
    """Embeddings using sentence-transformers (runs locally)."""

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        super().__init__(config)
        self._model = None

    async def initialize(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            model_name = self.config.model or "BAAI/bge-large-en-v1.5"
            self._model = SentenceTransformer(model_name, device=self.config.device)
            self.status = ProviderStatus.READY
            logger.info("Embedding model loaded: %s (%s)", model_name, self.config.device)
        except ImportError:
            logger.warning("sentence-transformers not installed. Install: pip install videomarker[search]")
            raise

    async def embed(self, texts: List[str]) -> List[List[float]]:
        if not self._model:
            raise RuntimeError("Provider not initialized")
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    async def embed_query(self, text: str) -> List[float]:
        return (await self.embed([text]))[0]
