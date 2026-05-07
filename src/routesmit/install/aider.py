"""Aider installer."""

from __future__ import annotations

from routesmit.install.base import BaseInstaller
from routesmit.types import InstallResult

AIDER_CONF_CONTENT = """\
# routesmit aider configuration
# Aider supports model switching via --model flag

# Recommended model for mixed tasks:
# model: claude-sonnet-4-20250514

# For planning-heavy tasks:
# model: claude-opus-4-20250514

# For fast formatting:
# model: claude-haiku-3-5-20241022
"""

AIDERIGNORE_ADDITION = """\
# routesmit generated files
.routesmit/
"""


class AiderInstaller(BaseInstaller):
    """Install routesmit configuration for Aider."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file(".aider.routesmit.yml", AIDER_CONF_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="aider",
            success=True,
            files_created=files_created,
            messages=[
                "Created .aider.routesmit.yml with model recommendations.",
                "Aider supports model switching via --model flag.",
                "Use routesmit explain to see recommended models per task.",
            ],
        )
