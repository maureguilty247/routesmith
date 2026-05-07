"""Copilot installer."""

from __future__ import annotations

from routesmit.install.base import BaseInstaller
from routesmit.types import InstallResult

COPILOT_INSTRUCTIONS_CONTENT = """\
# routesmit - Host-Aware Routing Instructions

This project uses routesmit for intelligent task routing.

## Core Principles

- routesmit is host-aware: it works WITHIN the host's supported model-control surface.
- Auto mode is the default for all mixed-task prompts.
- Model routing must stay within host capabilities.
- No fake cross-provider assumptions.
- If dynamic model switching is unavailable, use prompt strategy instead.

## Task Decomposition

When a prompt contains multiple task types, decompose into steps:
1. **Planning** - Design the approach (deep reasoning)
2. **Coding** - Implement the solution (coding capability)
3. **Testing** - Verify correctness (coding capability)
4. **Documentation** - Write docs (balanced capability)
5. **Review** - Final quality check (deep reasoning)

## Host Behavior

In Copilot/VS Code:
- Direct model switching from skill code is not reliably supported.
- Use structured prompts and clear task boundaries instead.
- Each subtask should be self-contained and well-specified.
- The planner/router/host-detection logic is deterministic and tested.

## Capability Classes

- `deep_reasoning` - Complex analysis, planning, review
- `coding` - Implementation, testing, refactoring
- `balanced` - Documentation, general tasks
- `fast` - Formatting, simple transformations
"""

PROMPT_FILE_CONTENT = """\
---
mode: agent
description: "Run routesmit task routing for a mixed prompt"
---

You are using routesmit's host-aware routing system.

For this task:
1. Identify all subtask types in the prompt (planning, coding, testing, docs, review)
2. Execute them in dependency order
3. Use structured, focused prompts for each step
4. Report which capability class each step ideally needs

Remember: routesmit does not assume cross-provider model access.
Work within the host's available models and capabilities.
"""


class CopilotInstaller(BaseInstaller):
    """Install routesmit configuration for GitHub Copilot."""

    def install(self) -> InstallResult:
        files_created: list[str] = []

        path = self._write_file(
            ".github/copilot-instructions.md",
            COPILOT_INSTRUCTIONS_CONTENT,
        )
        files_created.append(path)

        path = self._write_file(
            ".github/prompts/routesmit-route.prompt.md",
            PROMPT_FILE_CONTENT,
        )
        files_created.append(path)

        return InstallResult(
            target="copilot",
            success=True,
            files_created=files_created,
            messages=[
                "Created .github/copilot-instructions.md with routing guidance.",
                "Created .github/prompts/routesmit-route.prompt.md for agent mode.",
                "Copilot will use these files for task routing awareness.",
            ],
        )
