"""Abstract embedding provider."""

from __future__ import annotations

from abc import abstractmethod
from typing import List, Optional

from vdoc.providers.base import BaseProvider


class EmbeddingProvider(BaseProvider):
    """Vector embedding generation."""

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        ...

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a search query."""
        ...
