"""Cursor installer."""

from __future__ import annotations

from routesmith.install.base import BaseInstaller
from routesmith.types import InstallResult

CURSORULES_CONTENT = """\
# routesmith - Cursor Rules

This project uses routesmith for host-aware task routing.

## Principles

- Decompose mixed prompts into focused subtasks.
- Execute in dependency order: plan -> code -> test -> docs -> review.
- Model selection is user-controlled in Cursor.
- Use structured, clear prompts for each subtask.
- Do not assume cross-provider model access.

## Capability Mapping (advisory)

- Planning/Analysis/Review: Use strongest reasoning model available.
- Coding/Testing/Refactor: Use strongest coding model available.
- Documentation: Use balanced model.
- Formatting: Use fastest model.

## Task Types

Recognized task types: planning, analysis, coding, testing, refactor, documentation, formatting, review.
"""


class CursorInstaller(BaseInstaller):
    """Install routesmith configuration for Cursor."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file(".cursorules", CURSORULES_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="cursor",
            success=True,
            files_created=files_created,
            messages=[
                "Created .cursorules with routesmith guidance.",
                "Cursor will use these rules for routing awareness.",
            ],
        )
