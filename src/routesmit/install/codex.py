"""Codex installer."""

from __future__ import annotations

from routesmit.install.base import BaseInstaller
from routesmit.types import InstallResult

AGENTS_MD_CONTENT = """\
# routesmit

This project uses routesmit for host-aware task routing.

## Rules

- routesmit is a host-aware skill layer.
- In Codex/OpenAI environments, only OpenAI-family models are available.
- Auto mode is the default. Tasks are decomposed and routed to the best available OpenAI model.
- Model routing respects host constraints.
- Capability mapping:
  - Deep reasoning (planning, analysis, review) -> strongest reasoning model (e.g., o3)
  - Coding (implement, test, refactor) -> strongest coding model (e.g., codex-mini)
  - Documentation -> balanced model (e.g., gpt-4.1)
  - Formatting -> fastest model (e.g., gpt-4.1-mini)

## Task Decomposition

For mixed prompts, routesmit splits work into ordered subtasks.
Each step targets the most appropriate model from the OpenAI family.
"""


class CodexInstaller(BaseInstaller):
    """Install routesmit configuration for Codex."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file("AGENTS.md", AGENTS_MD_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="codex",
            success=True,
            files_created=files_created,
            messages=[
                "Created AGENTS.md with routesmit instructions.",
                "Codex will use these instructions for routing guidance.",
            ],
        )
