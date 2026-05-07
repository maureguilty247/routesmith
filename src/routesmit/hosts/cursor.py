"""Cursor host adapter."""

from __future__ import annotations

import os
from pathlib import Path

from routesmit.hosts.base import BaseHostAdapter
from routesmit.types import (
    CapabilityClass,
    HostCapabilities,
    HostDetectionResult,
    TaskNode,
)


class CursorHostAdapter(BaseHostAdapter):
    """Adapter for Cursor IDE."""

    MODEL_MAP: dict[CapabilityClass, str] = {
        CapabilityClass.DEEP_REASONING: "claude-sonnet-4",
        CapabilityClass.CODING: "claude-sonnet-4",
        CapabilityClass.BALANCED: "gpt-4.1",
        CapabilityClass.FAST: "cursor-small",
    }

    AVAILABLE_MODELS = [
        "claude-sonnet-4",
        "gpt-4.1",
        "gpt-4.1-mini",
        "cursor-small",
    ]

    def detect(self) -> HostDetectionResult:
        """Detect Cursor IDE environment."""
        confidence = 0.0
        method_parts: list[str] = []

        if os.environ.get("CURSOR_SESSION") or os.environ.get("CURSOR_ENV"):
            confidence += 0.5
            method_parts.append("CURSOR env")

        # Check for .cursor directory
        cwd = Path.cwd()
        if (cwd / ".cursor").exists() or (cwd / ".cursorules").exists():
            confidence += 0.3
            method_parts.append(".cursor/.cursorules")

        # Cursor also shows as vscode in some cases
        if os.environ.get("TERM_PROGRAM") == "vscode" and (cwd / ".cursor").exists():
            confidence += 0.2
            method_parts.append("vscode+cursor")

        return HostDetectionResult(
            host_name="cursor",
            confidence=min(confidence, 1.0),
            detection_method=", ".join(method_parts) if method_parts else "none",
            root_path=str(cwd),
        )

    def get_capabilities(self) -> HostCapabilities:
        """Get Cursor capabilities."""
        return HostCapabilities(
            host_name="cursor",
            detected=self.detect().confidence > 0.3,
            current_model=None,
            available_models=self.AVAILABLE_MODELS,
            supports_dynamic_switch=False,
            supports_prompt_files=True,
            supports_repo_instructions=True,
            supports_settings_edit=True,
            supports_env_override=False,
            model_family="mixed",
            notes=[
                "Cursor supports multiple model providers.",
                "Model selection is user-controlled via Cursor UI.",
                "Use .cursorules and prompt files for guidance.",
                "Direct model switching from skill code is not supported.",
            ],
        )

    def get_current_model(self) -> str | None:
        """Cursor model is user-controlled."""
        return None

    def get_available_models(self) -> list[str]:
        """Get models Cursor may support."""
        return self.AVAILABLE_MODELS.copy()

    def supports_dynamic_switch(self) -> bool:
        """Cursor does not support dynamic switching from skill code."""
        return False

    def set_model(self, model_name: str) -> bool:
        """Cannot switch models in Cursor from skill code."""
        return False

    def resolve_capability_class(self, capability: CapabilityClass) -> str | None:
        """Resolve capability class for Cursor."""
        return self.MODEL_MAP.get(capability)

    def apply_prompt_strategy(self, task: TaskNode) -> dict:
        """Generate prompt strategy for Cursor."""
        ideal_model = self.resolve_capability_class(task.preferred_capability_class)
        return {
            "task_id": task.id,
            "task_type": task.type.value,
            "strategy": "prompt_optimization",
            "target_model": None,
            "ideal_model_advisory": ideal_model,
            "hints": [
                f"Optimize prompt for {task.type.value} task in Cursor.",
                "Model switching is user-controlled in Cursor.",
                "Use .cursorules for persistent guidance.",
            ],
        }
