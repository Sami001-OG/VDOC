"""CacheManager — disk-backed caching abstraction.

Higher-level than the in-memory ResponseCache used inside providers.
Supports TTL, namespace isolation, and cache size limits.
"""

from __future__ import annotations

import hashlib
import json
import logging
import pickle
import time
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CacheEntry:
    def __init__(self, value: Any, ttl: float = 0) -> None:
        self.value = value
        self.created = time.monotonic()
        self.ttl = ttl

    @property
    def expired(self) -> bool:
        return self.ttl > 0 and (time.monotonic() - self.created) > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "ttl": self.ttl,
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CacheEntry:
        entry = cls(data["value"], data["ttl"])
        entry.created = data["created"]
        return entry


class CacheManager:
    """Multi-backend cache with TTL, namespaces, and optional persistence."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        default_ttl: float = 300,
        max_size_mb: int = 500,
    ) -> None:
        self._memory: Dict[str, CacheEntry] = {}
        self._cache_dir = Path(cache_dir) if cache_dir else None
        self._default_ttl = default_ttl
        self._max_size_mb = max_size_mb
        self._hits = 0
        self._misses = 0
        self._namespace_counters: Dict[str, int] = {}

    # -- Core API --

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        cache = self._namespace_key(namespace, key)
        # Try memory first
        if cache in self._memory:
            entry = self._memory[cache]
            if not entry.expired:
                self._hits += 1
                return entry.value
            del self._memory[cache]
        # Try disk
        if self._cache_dir:
            entry = self._load_from_disk(cache)
            if entry is not None and not entry.expired:
                self._memory[cache] = entry
                self._hits += 1
                return entry.value
        self._misses += 1
        return None

    def set(self, key: str, value: Any, namespace: str = "default", ttl: Optional[float] = None) -> None:
        cache = self._namespace_key(namespace, key)
        entry = CacheEntry(value, ttl or self._default_ttl)
        self._memory[cache] = entry
        if self._cache_dir:
            self._save_to_disk(cache, entry)
        self._namespace_counters[namespace] = self._namespace_counters.get(namespace, 0) + 1

    def invalidate(self, key: str, namespace: str = "default") -> None:
        cache = self._namespace_key(namespace, key)
        self._memory.pop(cache, None)
        if self._cache_dir:
            path = self._disk_path(cache)
            if path.exists():
                path.unlink()

    def invalidate_namespace(self, namespace: str) -> None:
        prefix = f"{namespace}:"
        self._memory = {k: v for k, v in self._memory.items() if not k.startswith(prefix)}
        if self._cache_dir:
            for p in self._cache_dir.glob(f"{namespace}_*.cache"):
                p.unlink()
        self._namespace_counters.pop(namespace, None)

    def clear(self) -> None:
        self._memory.clear()
        if self._cache_dir and self._cache_dir.exists():
            for p in self._cache_dir.glob("*.cache"):
                p.unlink()
        self._namespace_counters.clear()
        self._hits = 0
        self._misses = 0

    def get_or_compute(self, key: str, factory, namespace: str = "default", ttl: Optional[float] = None) -> Any:
        cached = self.get(key, namespace)
        if cached is not None:
            return cached
        value = factory()
        self.set(key, value, namespace, ttl)
        return value

    # -- Stats --

    @property
    def hit_ratio(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size_bytes(self) -> int:
        total = 0
        if self._cache_dir and self._cache_dir.exists():
            for p in self._cache_dir.glob("*.cache"):
                total += p.stat().st_size
        return total

    def stats(self) -> Dict[str, Any]:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio": self.hit_ratio,
            "memory_entries": len(self._memory),
            "disk_size_bytes": self.size_bytes,
            "disk_size_mb": round(self.size_bytes / 1024 / 1024, 2),
            "namespaces": dict(self._namespace_counters),
        }

    # -- Internal --

    def _namespace_key(self, namespace: str, key: str) -> str:
        return f"{namespace}:{key}"

    def _disk_path(self, cache_key: str) -> Path:
        assert self._cache_dir is not None
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256(cache_key.encode()).hexdigest()[:32]
        return self._cache_dir / f"{h}.cache"

    def _save_to_disk(self, cache_key: str, entry: CacheEntry) -> None:
        path = self._disk_path(cache_key)
        try:
            data = json.dumps({"value": pickle.dumps(entry.value).hex(), "ttl": entry.ttl, "created": entry.created})
            path.write_text(data)
        except Exception as e:
            logger.warning("Cache disk write failed for %s: %s", cache_key, e)

    def _load_from_disk(self, cache_key: str) -> Optional[CacheEntry]:
        path = self._disk_path(cache_key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            value = pickle.loads(bytes.fromhex(data["value"]))
            entry = CacheEntry(value, data["ttl"])
            entry.created = data["created"]
            if not entry.expired:
                return entry
            path.unlink()
        except Exception as e:
            logger.warning("Cache disk read failed for %s: %s", cache_key, e)
        return None
