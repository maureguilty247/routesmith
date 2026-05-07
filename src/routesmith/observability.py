"""Structured observability for routesmith - JSON logging and timing."""

from __future__ import annotations

import json
import logging
import sys
import time
from contextlib import contextmanager
from typing import Any, Generator


class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include extra fields
        for key in ("task_id", "model", "duration_ms", "phase", "host", "event"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def get_logger(name: str = "routesmith", structured: bool = False) -> logging.Logger:
    """Get a routesmith logger with optional structured output."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        if structured:
            handler.setFormatter(StructuredFormatter())
        else:
            handler.setFormatter(logging.Formatter(
                "[%(levelname)s] %(name)s: %(message)s"
            ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


@contextmanager
def timed(label: str, logger: logging.Logger | None = None) -> Generator[dict[str, float], None, None]:
    """Context manager that times a block and stores duration in a dict.

    Usage:
        with timed("planning") as t:
            do_planning()
        print(t["duration_ms"])
    """
    result: dict[str, float] = {"duration_ms": 0.0}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["duration_ms"] = (time.perf_counter() - start) * 1000
        if logger:
            logger.info(
                f"{label} completed",
                extra={"phase": label, "duration_ms": result["duration_ms"]},
            )


def log_task_execution(
    logger: logging.Logger,
    task_id: str,
    model: str | None,
    duration_ms: float,
    success: bool,
) -> None:
    """Log a structured task execution event."""
    logger.info(
        f"Task {task_id} {'succeeded' if success else 'failed'}",
        extra={
            "event": "task_execution",
            "task_id": task_id,
            "model": model,
            "duration_ms": duration_ms,
        },
    )


def log_route_complete(
    logger: logging.Logger,
    host: str,
    total_tasks: int,
    succeeded: int,
    total_ms: float,
) -> None:
    """Log a structured route completion event."""
    logger.info(
        f"Route complete: {succeeded}/{total_tasks} tasks in {total_ms:.1f}ms",
        extra={
            "event": "route_complete",
            "host": host,
            "duration_ms": total_ms,
        },
    )
