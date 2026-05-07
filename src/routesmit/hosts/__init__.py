"""Host adapters for routesmit."""

from routesmit.hosts.base import BaseHostAdapter
from routesmit.hosts.detector import detect_host, get_host_capabilities

__all__ = [
    "BaseHostAdapter",
    "detect_host",
    "get_host_capabilities",
]
