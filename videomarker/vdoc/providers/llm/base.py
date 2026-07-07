"""Abstract LLM provider."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from vdoc.providers.base import BaseProvider


class LLMProvider(BaseProvider):
    """Text generation and chat completion."""

    @abstractmethod
    async def complete(
        self, prompt: str, system: Optional[str] = None, **kwargs: Any
    ) -> str:
        """Generate text completion."""
        ...

    @abstractmethod
    async def chat(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> str:
        """Multi-turn chat completion."""
        ...

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings."""
        ...
