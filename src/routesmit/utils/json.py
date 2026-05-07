"""JSON utilities for routesmit."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel


def to_json(obj: Any, indent: int = 2) -> str:
    """Serialize an object to JSON string."""
    if isinstance(obj, BaseModel):
        return obj.model_dump_json(indent=indent)
    return json.dumps(obj, indent=indent, default=str)


def from_json(text: str) -> Any:
    """Parse a JSON string."""
    return json.loads(text)
