"""Gemini CLI installer."""

from __future__ import annotations

from routesmith.install.base import BaseInstaller
from routesmith.types import InstallResult

GEMINI_MD_CONTENT = """\
# routesmith

This project uses routesmith for host-aware task routing in Gemini CLI.

## Rules

- routesmith works within Gemini CLI's native model-switching surface.
- Auto mode is the default for mixed prompts.
- Decompose work into planning, coding, testing, documentation, and review steps.
- Use stronger Gemini models for deep reasoning and balanced or fast models for lower-cost steps.
- Keep routing truthful: if a capability is downgraded for cost, say so.

## Context

- Use Gemini-family models only.
- Respect repo-level context in GEMINI.md.
- Prefer focused prompts for each subtask and report the chosen capability class.
"""


class GeminiInstaller(BaseInstaller):
    """Install routesmith configuration for Gemini CLI."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file("GEMINI.md", GEMINI_MD_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="gemini",
            success=True,
            files_created=files_created,
            messages=[
                "Created GEMINI.md with routesmith guidance.",
                "Gemini CLI will use this file as persistent project context.",
            ],
        )