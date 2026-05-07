"""Logging utilities for routesmith."""

from __future__ import annotations

import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for routesmith modules."""
    logger = logging.getLogger(f"routesmith.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler()
        level = logging.DEBUG if os.environ.get("ROUTESMITH_DEBUG") else logging.WARNING
        handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(name)s] %(levelname)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
