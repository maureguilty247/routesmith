"""Generic host adapter - fallback when no specific host is detected."""

from __future__ import annotations

from pathlib import Path

from routesmith.hosts.base import BaseHostAdapter
from routesmith.types import (
    CapabilityClass,
    HostCapabilities,
    HostDetectionResult,
    TaskNode,
)


class GenericHostAdapter(BaseHostAdapter):
    """Fallback adapter when no specific host is detected.

    Does not fake model switching. Provides task decomposition
    and prompt guidance only.
    """

    def detect(self) -> HostDetectionResult:
        """Generic always matches with low confidence."""
        return HostDetectionResult(
            host_name="generic",
            confidence=0.1,
            detection_method="fallback",
            root_path=str(Path.cwd()),
        )

    def get_capabilities(self) -> HostCapabilities:
        """Get generic capabilities (minimal)."""
        return HostCapabilities(
            host_name="generic",
            detected=True,
            current_model=None,
            available_models=[],
            supports_dynamic_switch=False,
            supports_prompt_files=False,
            supports_repo_instructions=False,
            supports_settings_edit=False,
            supports_env_override=False,
            model_family="unknown",
            notes=[
                "No specific host detected.",
                "Model switching is not available.",
                "Task decomposition and prompt optimization will be used.",
            ],
        )

    def get_current_model(self) -> str | None:
        """No model detectable in generic mode."""
        return None

    def get_available_models(self) -> list[str]:
        """No models available in generic mode."""
        return []

    def supports_dynamic_switch(self) -> bool:
        """Generic does not support switching."""
        return False

    def set_model(self, model_name: str) -> bool:
        """Cannot switch models in generic mode."""
        return False

    def resolve_capability_class(self, capability: CapabilityClass) -> str | None:
        """No model resolution in generic mode."""
        return None

    def apply_prompt_strategy(self, task: TaskNode) -> dict:
        """Generate prompt-only strategy."""
        return {
            "task_id": task.id,
            "task_type": task.type.value,
            "strategy": "prompt_only",
            "target_model": None,
            "hints": [
                f"This is a {task.type.value} task: {task.title}",
                "No model switching available. Focus on clear prompt structure.",
                "Break down complex steps into smaller, focused instructions.",
            ],
        }
