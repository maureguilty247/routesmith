"""Host adapters for routesmith."""

from routesmith.hosts.base import BaseHostAdapter
from routesmith.hosts.detector import detect_host, get_host_capabilities
from routesmith.hosts.gemini_cli import GeminiCLIHostAdapter

__all__ = [
    "BaseHostAdapter",
    "detect_host",
    "get_host_capabilities",
    "GeminiCLIHostAdapter",
]
