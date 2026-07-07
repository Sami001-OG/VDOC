"""MemoryMonitor — memory usage tracking and metrics collection."""

from __future__ import annotations

import gc
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    timestamp: float = 0.0
    rss_mb: float = 0.0
    vms_mb: float = 0.0
    gc_objects: int = 0
    gc_collections: int = 0


class MemoryMonitor:
    """Periodically captures memory usage for profiling and alerting."""

    def __init__(self, interval: float = 5.0, max_samples: int = 1000) -> None:
        self._interval = interval
        self._max_samples = max_samples
        self._snapshots: List[MemorySnapshot] = []
        self._running = False
        self._peak_rss = 0.0
        self._collection_count = 0

    @property
    def snapshots(self) -> List[MemorySnapshot]:
        return list(self._snapshots)

    @property
    def peak_rss_mb(self) -> float:
        return self._peak_rss

    @property
    def current_rss_mb(self) -> float:
        return self._sample().rss_mb

    def _sample(self) -> MemorySnapshot:
        import psutil
        proc = psutil.Process(os.getpid())
        mem = proc.memory_info()
        rss = mem.rss / (1024 * 1024)
        vms = mem.vms / (1024 * 1024)
        gc_count = len(gc.get_objects())
        self._peak_rss = max(self._peak_rss, rss)
        return MemorySnapshot(
            timestamp=time.time(),
            rss_mb=round(rss, 2),
            vms_mb=round(vms, 2),
            gc_objects=gc_count,
            gc_collections=self._collection_count,
        )

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        logger.info("MemoryMonitor started (interval=%ss)", self._interval)

    def stop(self) -> List[MemorySnapshot]:
        self._running = False
        logger.info("MemoryMonitor stopped (%d snapshots)", len(self._snapshots))
        return self._snapshots

    def tick(self) -> MemorySnapshot:
        snap = self._sample()
        self._snapshots.append(snap)
        if len(self._snapshots) > self._max_samples:
            self._snapshots.pop(0)
        return snap

    def collect_garbage(self) -> int:
        count = gc.collect()
        self._collection_count += count
        return count

    def summary(self) -> Dict[str, Any]:
        if not self._snapshots:
            return {"status": "no_data"}
        rss_values = [s.rss_mb for s in self._snapshots]
        return {
            "peak_rss_mb": self._peak_rss,
            "avg_rss_mb": round(sum(rss_values) / len(rss_values), 2),
            "min_rss_mb": round(min(rss_values), 2),
            "current_rss_mb": round(rss_values[-1], 2),
            "samples": len(self._snapshots),
            "gc_collections": self._collection_count,
            "duration_sec": round(self._snapshots[-1].timestamp - self._snapshots[0].timestamp, 2)
            if len(self._snapshots) > 1
            else 0,
        }
