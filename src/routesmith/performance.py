"""Real-time model performance tracking for routesmith.

Records per-model task outcomes across runs and provides performance
stats that can inform routing decisions.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from routesmith.types import CapabilityClass, RoutePlan, TaskResult, TaskType


@dataclass(slots=True)
class ModelRecord:
    """A single recorded task outcome for a model."""

    model: str
    task_type: str
    capability_class: str
    success: bool
    duration_ms: float
    timestamp: float


@dataclass(slots=True)
class ModelStats:
    """Aggregated performance statistics for a model."""

    model: str
    total_tasks: int = 0
    successes: int = 0
    failures: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    task_types: dict[str, int] = field(default_factory=dict)
    capability_classes: dict[str, int] = field(default_factory=dict)
    last_used: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "total_tasks": self.total_tasks,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": round(self.success_rate, 3),
            "avg_duration_ms": round(self.avg_duration_ms, 1),
            "min_duration_ms": round(self.min_duration_ms, 1),
            "max_duration_ms": round(self.max_duration_ms, 1),
            "task_types": self.task_types,
            "capability_classes": self.capability_classes,
            "last_used": self.last_used,
        }


class PerformanceTracker:
    """Tracks and persists model performance across runs.

    Data is stored in a local JSON file so it accumulates over time
    within a project.
    """

    DEFAULT_PATH = ".routesmith/performance.json"
    MAX_RECORDS = 500  # Rolling window of recent records

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else Path(self.DEFAULT_PATH)
        self._records: list[ModelRecord] = []
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text())
            for entry in data.get("records", []):
                self._records.append(ModelRecord(
                    model=entry["model"],
                    task_type=entry["task_type"],
                    capability_class=entry["capability_class"],
                    success=entry["success"],
                    duration_ms=entry["duration_ms"],
                    timestamp=entry["timestamp"],
                ))
        except (OSError, json.JSONDecodeError, KeyError):
            # Corrupted file — start fresh
            self._records = []

    def record_run(self, plan: RoutePlan, results: list[TaskResult]) -> None:
        """Record task outcomes from a completed run."""
        self._ensure_loaded()
        task_map = {t.id: t for t in plan.tasks}
        now = time.time()

        for result in results:
            task_node = task_map.get(result.task_id)
            if not task_node:
                continue
            model = result.model_used or "unknown"
            self._records.append(ModelRecord(
                model=model,
                task_type=task_node.type.value,
                capability_class=task_node.preferred_capability_class.value,
                success=result.success,
                duration_ms=result.duration_ms,
                timestamp=now,
            ))

        # Trim to rolling window
        if len(self._records) > self.MAX_RECORDS:
            self._records = self._records[-self.MAX_RECORDS:]

        self._persist()

    def _persist(self) -> None:
        """Write records to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 1,
            "updated": time.time(),
            "records": [
                {
                    "model": r.model,
                    "task_type": r.task_type,
                    "capability_class": r.capability_class,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "timestamp": r.timestamp,
                }
                for r in self._records
            ],
        }
        self.path.write_text(json.dumps(data, indent=2))

    def get_model_stats(self, model: str | None = None) -> list[ModelStats]:
        """Get aggregated stats, optionally filtered to a single model."""
        self._ensure_loaded()
        grouped: dict[str, list[ModelRecord]] = {}
        for record in self._records:
            if model and record.model != model:
                continue
            grouped.setdefault(record.model, []).append(record)

        stats: list[ModelStats] = []
        for model_name, records in sorted(grouped.items()):
            durations = [r.duration_ms for r in records]
            successes = sum(1 for r in records if r.success)
            total = len(records)

            task_types: dict[str, int] = {}
            cap_classes: dict[str, int] = {}
            for r in records:
                task_types[r.task_type] = task_types.get(r.task_type, 0) + 1
                cap_classes[r.capability_class] = cap_classes.get(r.capability_class, 0) + 1

            stats.append(ModelStats(
                model=model_name,
                total_tasks=total,
                successes=successes,
                failures=total - successes,
                success_rate=successes / total if total > 0 else 0.0,
                avg_duration_ms=sum(durations) / total if total > 0 else 0.0,
                min_duration_ms=min(durations) if durations else 0.0,
                max_duration_ms=max(durations) if durations else 0.0,
                task_types=task_types,
                capability_classes=cap_classes,
                last_used=max(r.timestamp for r in records),
            ))
        return stats

    def get_capability_stats(self, capability: CapabilityClass | str | None = None) -> dict[str, Any]:
        """Get performance breakdown by capability class."""
        self._ensure_loaded()
        cap_value = capability.value if isinstance(capability, CapabilityClass) else capability

        grouped: dict[str, list[ModelRecord]] = {}
        for record in self._records:
            if cap_value and record.capability_class != cap_value:
                continue
            grouped.setdefault(record.capability_class, []).append(record)

        result: dict[str, Any] = {}
        for cap_name, records in sorted(grouped.items()):
            models: dict[str, dict[str, Any]] = {}
            for r in records:
                entry = models.setdefault(r.model, {"tasks": 0, "successes": 0, "total_ms": 0.0})
                entry["tasks"] += 1
                if r.success:
                    entry["successes"] += 1
                entry["total_ms"] += r.duration_ms

            result[cap_name] = {
                "total_tasks": len(records),
                "success_rate": sum(1 for r in records if r.success) / len(records) if records else 0.0,
                "models": {
                    m: {
                        "tasks": d["tasks"],
                        "success_rate": d["successes"] / d["tasks"] if d["tasks"] else 0.0,
                        "avg_duration_ms": round(d["total_ms"] / d["tasks"], 1) if d["tasks"] else 0.0,
                    }
                    for m, d in models.items()
                },
            }
        return result

    def get_performance_advisory(self) -> list[str]:
        """Generate advisory messages based on tracked performance data."""
        self._ensure_loaded()
        if not self._records:
            return []

        advisory: list[str] = []
        stats = self.get_model_stats()

        for s in stats:
            if s.model == "unknown":
                continue
            if s.total_tasks >= 5 and s.success_rate < 0.7:
                advisory.append(
                    f"Model {s.model} has a low success rate ({s.success_rate:.0%}) "
                    f"across {s.total_tasks} tracked tasks."
                )
            if s.total_tasks >= 5 and s.avg_duration_ms > 5000:
                advisory.append(
                    f"Model {s.model} averages {s.avg_duration_ms:.0f}ms per task — "
                    "consider a faster model for latency-sensitive work."
                )

        return advisory

    def clear(self) -> None:
        """Clear all tracked performance data."""
        self._records = []
        self._loaded = True
        if self.path.exists():
            self.path.unlink()

    def summary_dict(self) -> dict[str, Any]:
        """Return a complete summary suitable for serialization or display."""
        self._ensure_loaded()
        return {
            "total_records": len(self._records),
            "models": [s.to_dict() for s in self.get_model_stats()],
            "by_capability": self.get_capability_stats(),
            "advisory": self.get_performance_advisory(),
        }
