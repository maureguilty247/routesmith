"""Generic installer."""

from __future__ import annotations

from routesmit.install.base import BaseInstaller
from routesmit.types import InstallResult

ROUTESMIT_CONFIG_CONTENT = """\
# routesmit configuration
# This file provides routing guidance for unknown/generic host environments.

# Default mode: auto (recommended)
# In auto mode, routesmit decomposes prompts and optimizes per subtask.

# Since no specific host was detected:
# - Model switching is not available
# - Task decomposition and prompt optimization will be used
# - Use `routesmit explain "<prompt>"` to see the route plan

# Capability classes:
# - deep_reasoning: planning, analysis, review
# - coding: implementation, testing, refactoring
# - balanced: documentation, general
# - fast: formatting, simple transforms
"""


class GenericInstaller(BaseInstaller):
    """Install routesmit configuration for generic/unknown hosts."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file(".routesmit.yml", ROUTESMIT_CONFIG_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="generic",
            success=True,
            files_created=files_created,
            messages=[
                "Created .routesmit.yml with generic configuration.",
                "Use `routesmit explain` to see route plans without execution.",
            ],
        )
