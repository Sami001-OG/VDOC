"""Abstract base class for all providers with retry, caching, rate-limiting."""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class ProviderStatus(str, Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    CLOSED = "closed"


class ProviderCapability(str, Enum):
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    STREAMING = "streaming"
    EMBEDDING = "embedding"
    IMAGE_DESCRIPTION = "image_description"
    IMAGE_BATCH = "image_batch"
    SPEECH_TO_TEXT = "speech_to_text"
    OCR = "ocr"
    VIDEO_LOADING = "video_loading"
    SEARCH = "search"


class ProviderConfig(BaseModel):
    """Base configuration for all providers."""

    name: str
    model: str = ""
    device: str = "cpu"
    max_retries: int = 3
    timeout: int = 120
    batch_size: int = 1
    rate_limit: int = 0
    cache_ttl: int = 0
    fallbacks: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable[[F], F]:
    """Decorator: retry a function on failure with exponential backoff."""
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        wait = delay * (backoff ** attempt)
                        logger.warning("%s failed (attempt %d/%d), retrying in %.1fs: %s",
                                       func.__name__, attempt + 1, max_attempts, wait, e)
                        await asyncio.sleep(wait)
            raise last_exc  # type: ignore
        return wrapper  # type: ignore
    return decorator


class ResponseCache:
    """Simple in-memory response cache with TTL."""

    def __init__(self, default_ttl: int = 300) -> None:
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            expires, value = self._cache[key]
            if time.monotonic() < expires:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._cache[key] = (time.monotonic() + (ttl or self._default_ttl), value)

    def clear(self) -> None:
        self._cache.clear()

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)


class RateLimiter:
    """Token-bucket rate limiter."""

    def __init__(self, max_per_second: int = 0) -> None:
        self._max = max_per_second
        self._tokens = float(max_per_second)
        self._last = time.monotonic()

    async def acquire(self) -> None:
        if self._max <= 0:
            return
        now = time.monotonic()
        elapsed = now - self._last
        self._tokens = min(float(self._max), self._tokens + elapsed * self._max)
        self._last = now
        if self._tokens < 1:
            wait = (1 - self._tokens) / self._max
            await asyncio.sleep(wait)
            self._tokens = 0
        else:
            self._tokens -= 1


class BaseProvider(ABC):
    """Every provider inherits from this.

    Features:
        - Retry with exponential backoff (#24)
        - Rate limiting (#25)
        - Response caching (#28)
        - Capability detection (#22)
        - Health checks (#23)
        - Streaming support (#27)
        - Provider metadata (#21)
    """

    capabilities: Set[ProviderCapability] = set()

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        self.config = config or ProviderConfig(name=self.__class__.__name__)
        self.status = ProviderStatus.UNINITIALIZED
        self._metadata: Dict[str, Any] = {}
        self._cache = ResponseCache(default_ttl=self.config.cache_ttl or 300)
        self._rate_limiter = RateLimiter(max_per_second=self.config.rate_limit)
        self._fallback_providers: List[BaseProvider] = []

    # --- Lifecycle ---

    @abstractmethod
    async def initialize(self) -> None:
        ...

    async def close(self) -> None:
        self.status = ProviderStatus.CLOSED
        self._cache.clear()

    @property
    def is_ready(self) -> bool:
        return self.status == ProviderStatus.READY

    # --- Capabilities (#22) ---

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities

    def list_capabilities(self) -> Set[ProviderCapability]:
        return self.capabilities

    # --- Health (#23) ---

    async def health_check(self) -> bool:
        try:
            result = await self._health_check_impl()
            self.status = ProviderStatus.READY if result else ProviderStatus.ERROR
            return result
        except Exception:
            self.status = ProviderStatus.ERROR
            return False

    async def _health_check_impl(self) -> bool:
        return self.status == ProviderStatus.READY

    # --- Rate limiting (#25) ---

    async def _throttle(self) -> None:
        await self._rate_limiter.acquire()

    # --- Caching (#28) ---

    def _cache_key(self, **kwargs: Any) -> str:
        return f"{self.config.name}:{hash(frozenset(kwargs.items()))}"

    async def _cached(self, key: str, factory: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        result = await factory()
        self._cache.set(key, result, ttl=ttl)
        return result

    # --- Streaming (#27) ---

    async def stream(self, **kwargs: Any) -> Any:
        raise NotImplementedError(f"{self.__class__.__name__} does not support streaming")

    # --- Fallback (#29) ---

    def set_fallbacks(self, providers: List[BaseProvider]) -> None:
        self._fallback_providers = providers

    async def _with_fallback(self, primary_call: Callable, **kwargs: Any) -> Any:
        try:
            return await primary_call()
        except Exception as e:
            for fb in self._fallback_providers:
                try:
                    logger.info("Falling back to %s", fb.config.name)
                    return await fb.process(**kwargs)
                except Exception:
                    continue
            raise

    # --- Metadata ---

    def get_metadata(self) -> Dict[str, Any]:
        return {
            **self._metadata,
            "name": self.config.name,
            "model": self.config.model,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "fallbacks": self.config.fallbacks,
        }
