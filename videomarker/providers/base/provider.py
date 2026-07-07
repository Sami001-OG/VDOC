"""Abstract base class for all providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ProviderStatus(str, Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    CLOSED = "closed"


class ProviderConfig(BaseModel):
    """Base configuration for all providers."""

    name: str
    model: str = ""
    device: str = "cpu"
    max_retries: int = 3
    timeout: int = 120
    batch_size: int = 1
    extra: Dict[str, Any] = Field(default_factory=dict)


class BaseProvider(ABC):
    """Every provider (LLM, speech, vision, OCR, embedding) inherits from this.

    Lifecycle:
        initialize() → process() → close()
    """

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        self.config = config or ProviderConfig(name=self.__class__.__name__)
        self.status = ProviderStatus.UNINITIALIZED
        self._metadata: Dict[str, Any] = {}

    @abstractmethod
    async def initialize(self) -> None:
        """Allocate resources, load models, open connections."""
        ...

    @abstractmethod
    async def process(self, **kwargs: Any) -> Any:
        """Run inference or processing."""
        ...

    async def close(self) -> None:
        """Release resources, close connections."""
        self.status = ProviderStatus.CLOSED

    @property
    def is_ready(self) -> bool:
        return self.status == ProviderStatus.READY

    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata
