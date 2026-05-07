"""Text utilities for routesmith."""

from __future__ import annotations


def truncate(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def indent(text: str, prefix: str = "  ") -> str:
    """Indent each line of text."""
    lines = text.split("\n")
    return "\n".join(prefix + line for line in lines)
