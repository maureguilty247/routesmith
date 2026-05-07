"""Base installer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from routesmith.types import InstallResult


class BaseInstaller(ABC):
    """Abstract base class for install adapters."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.cwd()

    @abstractmethod
    def install(self) -> InstallResult:
        """Run the installation."""
        ...

    def _write_file(self, relative_path: str, content: str) -> str:
        """Write a file relative to root. Creates directories as needed."""
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)
