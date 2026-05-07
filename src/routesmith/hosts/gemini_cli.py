"""Gemini CLI host adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path

from routesmith.hosts.base import BaseHostAdapter
from routesmith.types import (
    CapabilityClass,
    HostCapabilities,
    HostDetectionResult,
    TaskNode,
)


class GeminiCLIHostAdapter(BaseHostAdapter):
    """Adapter for Google Gemini CLI environments."""

    MODEL_MAP: dict[CapabilityClass, str] = {
        CapabilityClass.DEEP_REASONING: "gemini-3.1-pro",
        CapabilityClass.CODING: "gemini-3.1-pro",
        CapabilityClass.BALANCED: "gemini-3.1-flash",
        CapabilityClass.FAST: "gemini-3.1-flash-lite",
    }

    AVAILABLE_MODELS = [
        "gemini-3.1-pro",
        "gemini-3.1-flash",
        "gemini-3.1-flash-lite",
    ]

    def detect(self) -> HostDetectionResult:
        """Detect Gemini CLI environment."""
        confidence = 0.0
        method_parts: list[str] = []

        if os.environ.get("GEMINI_CLI"):
            confidence += 0.5
            method_parts.append("GEMINI_CLI env")

        if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
            confidence += 0.2
            method_parts.append("Gemini API key env")

        gemini_dir = Path.home() / ".gemini"
        if gemini_dir.exists():
            confidence += 0.2
            method_parts.append(".gemini dir")

        cwd = Path.cwd()
        if (cwd / "GEMINI.md").exists():
            confidence += 0.2
            method_parts.append("GEMINI.md")

        return HostDetectionResult(
            host_name="gemini_cli",
            confidence=min(confidence, 1.0),
            detection_method=", ".join(method_parts) if method_parts else "none",
            root_path=str(cwd),
        )

    def get_capabilities(self) -> HostCapabilities:
        """Get Gemini CLI capabilities."""
        return HostCapabilities(
            host_name="gemini_cli",
            detected=self.detect().confidence > 0.3,
            current_model=self._detect_current_model(),
            available_models=self.AVAILABLE_MODELS,
            supports_dynamic_switch=True,
            supports_prompt_files=True,
            supports_repo_instructions=True,
            supports_settings_edit=True,
            supports_env_override=True,
            model_family="google",
            notes=[
                "Gemini CLI supports Gemini-family models only.",
                "Model can be selected with the -m flag or persisted in ~/.gemini/settings.json.",
                "GEMINI.md repo instructions are supported.",
                "Gemini CLI can authenticate with Gemini API keys or Google-hosted auth flows.",
            ],
        )

    def get_current_model(self) -> str | None:
        """Detect the current Gemini model if possible."""
        return self._detect_current_model()

    def _detect_current_model(self) -> str | None:
        model = os.environ.get("GEMINI_MODEL")
        if model:
            return model
        settings_path = Path.home() / ".gemini" / "settings.json"
        if settings_path.exists():
            try:
                settings = json.loads(settings_path.read_text())
                return settings.get("model")
            except (OSError, json.JSONDecodeError):
                pass
        return None

    def get_available_models(self) -> list[str]:
        """Get available Gemini models."""
        return self.AVAILABLE_MODELS.copy()

    def supports_dynamic_switch(self) -> bool:
        """Gemini CLI supports model switching."""
        return True

    def set_model(self, model_name: str) -> bool:
        """Persist model selection to ~/.gemini/settings.json.

        Note: This mutates user-global state outside the project directory.
        """
        if model_name not in self.AVAILABLE_MODELS:
            return False

        settings_path = Path.home() / ".gemini" / "settings.json"
        try:
            settings: dict[str, object] = {}
            if settings_path.exists():
                settings = json.loads(settings_path.read_text())
            settings["model"] = model_name
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            settings_path.write_text(json.dumps(settings, indent=2))
            os.environ["GEMINI_MODEL"] = model_name
            return True
        except (OSError, json.JSONDecodeError):
            return False

    def resolve_capability_class(self, capability: CapabilityClass) -> str | None:
        """Resolve capability class to Gemini model."""
        return self.MODEL_MAP.get(capability)

    def apply_prompt_strategy(self, task: TaskNode) -> dict:
        """Generate Gemini CLI-specific prompt strategy hints."""
        model = self.resolve_capability_class(task.preferred_capability_class)
        return {
            "task_id": task.id,
            "task_type": task.type.value,
            "strategy": "model_switch",
            "target_model": model,
            "hints": [
                f"Use gemini -m {model} for {task.type.value} tasks.",
                "Gemini CLI supports custom context via GEMINI.md.",
            ],
        }