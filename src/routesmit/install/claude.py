"""Claude Code installer."""

from __future__ import annotations

from routesmit.install.base import BaseInstaller
from routesmit.types import InstallResult

CLAUDE_MD_CONTENT = """\
# routesmit

This project uses routesmit for host-aware task routing.

## Rules

- routesmit is a host-aware skill layer, not a cross-provider broker.
- In Claude Code, only Claude-family models are available.
- Auto mode is the default. Tasks are decomposed and routed to the best available Claude model.
- Model routing respects host constraints: no fake cross-provider switching.
- If model switching is supported, use the best model per task type:
  - Deep reasoning tasks (planning, analysis, review) -> strongest reasoning model
  - Coding tasks (implement, test, refactor) -> strongest coding model
  - Documentation -> balanced model
  - Formatting -> fastest model

## Task Decomposition

For mixed prompts, routesmit splits work into subtasks:
1. Planning
2. Implementation
3. Testing
4. Documentation
5. Review

Each step uses the most appropriate model from the Claude family.
"""


class ClaudeInstaller(BaseInstaller):
    """Install routesmit configuration for Claude Code."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        # Write CLAUDE.md
        path = self._write_file("CLAUDE.md", CLAUDE_MD_CONTENT)
        files_created.append(path)

        return InstallResult(
            target="claude",
            success=True,
            files_created=files_created,
            messages=[
                "Created CLAUDE.md with routesmit instructions.",
                "Claude Code will use these instructions for routing guidance.",
            ],
        )
