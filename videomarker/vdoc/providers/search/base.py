from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class SearchProvider(ABC):
    """Abstract interface for vector search operations."""

    @abstractmethod
    def build_index(self, vectors: List[List[float]], documents: List[Dict[str, Any]]) -> None:
        ...

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def add(self, vector: List[float], document: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def save(self, path: str) -> None:
        ...

    @abstractmethod
    def load(self, path: str) -> None:
        ...

    @property
    @abstractmethod
    def size(self) -> int:
        ...
