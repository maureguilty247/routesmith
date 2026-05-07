"""VS Code installer."""

from __future__ import annotations

from routesmith.install.base import BaseInstaller
from routesmith.types import InstallResult

COPILOT_INSTRUCTIONS_CONTENT = """\
# routesmith - VS Code / Copilot Instructions

This workspace uses routesmith for host-aware task routing.

## How it works

- routesmith decomposes mixed prompts into focused subtasks.
- Each task type maps to a capability class (deep_reasoning, coding, balanced, fast).
- In VS Code/Copilot, model switching is host-controlled.
- routesmith provides structured prompts and task decomposition instead.

## Usage

For any mixed-task prompt, routesmith will:
1. Classify the prompt into task types
2. Create a dependency-ordered task graph
3. Recommend the ideal capability class per step
4. Execute with optimized prompts per subtask
"""


class VSCodeInstaller(BaseInstaller):
    """Install routesmith configuration for VS Code."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file(
            ".github/copilot-instructions.md",
            COPILOT_INSTRUCTIONS_CONTENT,
        )
        files_created.append(path)

        return InstallResult(
            target="vscode",
            success=True,
            files_created=files_created,
            messages=[
                "Created .github/copilot-instructions.md for VS Code / Copilot.",
            ],
        )
