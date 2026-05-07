"""Aider installer."""

from __future__ import annotations

from routesmith.install.base import BaseInstaller
from routesmith.types import InstallResult

AIDER_CONF_CONTENT = """\
# routesmith aider configuration
# Aider supports model switching via --model flag

# Recommended model for mixed tasks:
# model: claude-sonnet-4-20250514

# For planning-heavy tasks:
# model: claude-opus-4-20250514

# For fast formatting:
# model: claude-haiku-3-5-20241022
"""

AIDERIGNORE_ADDITION = """\
# routesmith generated files
.routesmith/
"""


class AiderInstaller(BaseInstaller):
    """Install routesmith configuration for Aider."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file(".aider.routesmith.yml", AIDER_CONF_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="aider",
            success=True,
            files_created=files_created,
            messages=[
                "Created .aider.routesmith.yml with model recommendations.",
                "Aider supports model switching via --model flag.",
                "Use routesmith explain to see recommended models per task.",
            ],
        )
