"""GitHub Copilot host adapter."""

from __future__ import annotations

import os
from pathlib import Path

from routesmit.hosts.base import BaseHostAdapter
from routesmit.types import (
    CapabilityClass,
    HostCapabilities,
    HostDetectionResult,
    RoutePlan,
    TaskNode,
)


class CopilotHostAdapter(BaseHostAdapter):
    """Adapter for GitHub Copilot / VS Code environments."""

    # Copilot may expose multiple models but switching is host-controlled
    MODEL_MAP: dict[CapabilityClass, str] = {
        CapabilityClass.DEEP_REASONING: "claude-sonnet-4",
        CapabilityClass.CODING: "claude-sonnet-4",
        CapabilityClass.BALANCED: "gpt-4.1",
        CapabilityClass.FAST: "gpt-4.1-mini",
    }

    AVAILABLE_MODELS = [
        "claude-sonnet-4",
        "gpt-4.1",
        "gpt-4.1-mini",
        "o3-mini",
    ]

    def detect(self) -> HostDetectionResult:
        """Detect GitHub Copilot environment."""
        confidence = 0.0
        method_parts: list[str] = []

        # VS Code / Copilot indicators
        if os.environ.get("VSCODE_PID") or os.environ.get("TERM_PROGRAM") == "vscode":
            confidence += 0.4
            method_parts.append("VSCODE env")

        if os.environ.get("GITHUB_COPILOT"):
            confidence += 0.4
            method_parts.append("GITHUB_COPILOT env")

        # Check for .github/copilot-instructions.md
        cwd = Path.cwd()
        if (cwd / ".github" / "copilot-instructions.md").exists():
            confidence += 0.2
            method_parts.append("copilot-instructions.md")

        # Check for .vscode directory
        if (cwd / ".vscode").exists():
            confidence += 0.1
            method_parts.append(".vscode dir")

        return HostDetectionResult(
            host_name="copilot",
            confidence=min(confidence, 1.0),
            detection_method=", ".join(method_parts) if method_parts else "none",
            root_path=str(cwd),
        )

    def get_capabilities(self) -> HostCapabilities:
        """Get Copilot capabilities."""
        return HostCapabilities(
            host_name="copilot",
            detected=self.detect().confidence > 0.3,
            current_model=None,
            available_models=self.AVAILABLE_MODELS,
            supports_dynamic_switch=False,
            supports_prompt_files=True,
            supports_repo_instructions=True,
            supports_settings_edit=False,
            supports_env_override=False,
            model_family="mixed",
            notes=[
                "Copilot model selection is controlled by the host IDE.",
                "Direct model switching from skill code is not reliably supported.",
                "Use .github/copilot-instructions.md and prompt files for guidance.",
                "Task decomposition and prompt optimization are the primary strategies.",
            ],
        )

    def get_current_model(self) -> str | None:
        """Copilot model is host-controlled; may not be detectable."""
        return None

    def get_available_models(self) -> list[str]:
        """Get models that Copilot may support."""
        return self.AVAILABLE_MODELS.copy()

    def supports_dynamic_switch(self) -> bool:
        """Copilot does not support dynamic model switching from skill code."""
        return False

    def set_model(self, model_name: str) -> bool:
        """Cannot switch models in Copilot from skill code."""
        return False

    def resolve_capability_class(self, capability: CapabilityClass) -> str | None:
        """Resolve capability class - advisory only in Copilot."""
        return self.MODEL_MAP.get(capability)

    def apply_prompt_strategy(self, task: TaskNode) -> dict:
        """Generate prompt-based strategy for Copilot (no model switching)."""
        ideal_model = self.resolve_capability_class(task.preferred_capability_class)
        return {
            "task_id": task.id,
            "task_type": task.type.value,
            "strategy": "prompt_optimization",
            "target_model": None,
            "ideal_model_advisory": ideal_model,
            "hints": [
                f"Optimize prompt for {task.type.value} task.",
                "Model switching is not available in Copilot.",
                f"Ideal model would be {ideal_model} but host controls selection.",
                "Focus on clear, structured prompts for best results.",
            ],
        }

    def apply_repo_instructions(self, route_plan: RoutePlan) -> None:
        """Generate repo instruction recommendations for Copilot."""
        # In a real implementation, this could write .github/copilot-instructions.md
        pass
