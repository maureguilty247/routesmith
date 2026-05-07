"""Codex installer."""

from __future__ import annotations

from routesmith.install.base import BaseInstaller
from routesmith.types import InstallResult

AGENTS_MD_CONTENT = """\
# routesmith

This project uses routesmith for host-aware task routing.

## Rules

- routesmith is a host-aware skill layer.
- In Codex/OpenAI environments, only OpenAI-family models are available.
- Auto mode is the default. Tasks are decomposed and routed to the best available OpenAI model.
- Model routing respects host constraints.
- Capability mapping:
    - Deep reasoning (planning, analysis, review) -> strongest reasoning model (e.g., gpt-5.5; fall back to gpt-5.4)
    - Coding (implement, test, refactor) -> strongest coding model (e.g., gpt-5.3-codex)
    - Documentation -> balanced model (e.g., gpt-5.4)
    - Formatting -> fastest model (e.g., gpt-5.4-mini)

## Task Decomposition

For mixed prompts, routesmith splits work into ordered subtasks.
Each step targets the most appropriate model from the OpenAI family.
"""


class CodexInstaller(BaseInstaller):
    """Install routesmith configuration for Codex."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file("AGENTS.md", AGENTS_MD_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="codex",
            success=True,
            files_created=files_created,
            messages=[
                "Created AGENTS.md with routesmith instructions.",
                "Codex will use these instructions for routing guidance.",
            ],
        )
