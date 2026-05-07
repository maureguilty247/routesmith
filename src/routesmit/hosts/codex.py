"""OpenAI Codex host adapter."""

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


class CodexHostAdapter(BaseHostAdapter):
    """Adapter for OpenAI Codex CLI / OpenAI-native environments."""

    MODEL_MAP: dict[CapabilityClass, str] = {
        CapabilityClass.DEEP_REASONING: "o3",
        CapabilityClass.CODING: "codex-mini",
        CapabilityClass.BALANCED: "gpt-4.1",
        CapabilityClass.FAST: "gpt-4.1-mini",
    }

    AVAILABLE_MODELS = [
        "o3",
        "codex-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
    ]

    def detect(self) -> HostDetectionResult:
        """Detect Codex/OpenAI environment."""
        confidence = 0.0
        method_parts: list[str] = []

        if os.environ.get("CODEX_ENV") or os.environ.get("OPENAI_CODEX"):
            confidence += 0.5
            method_parts.append("CODEX_ENV/OPENAI_CODEX env")

        if os.environ.get("OPENAI_API_KEY"):
            confidence += 0.2
            method_parts.append("OPENAI_API_KEY")

        # Check for codex config
        codex_config = Path.home() / ".codex"
        if codex_config.exists():
            confidence += 0.3
            method_parts.append(".codex dir")

        # Check for AGENTS.md (Codex convention)
        cwd = Path.cwd()
        if (cwd / "AGENTS.md").exists():
            confidence += 0.2
            method_parts.append("AGENTS.md")

        return HostDetectionResult(
            host_name="codex",
            confidence=min(confidence, 1.0),
            detection_method=", ".join(method_parts) if method_parts else "none",
            root_path=str(cwd),
        )

    def get_capabilities(self) -> HostCapabilities:
        """Get Codex capabilities."""
        return HostCapabilities(
            host_name="codex",
            detected=self.detect().confidence > 0.3,
            current_model=self._detect_current_model(),
            available_models=self.AVAILABLE_MODELS,
            supports_dynamic_switch=True,
            supports_prompt_files=True,
            supports_repo_instructions=True,
            supports_settings_edit=False,
            supports_env_override=True,
            model_family="openai",
            notes=[
                "Codex supports OpenAI-family models only.",
                "Model can be set via CLI flags or environment.",
                "AGENTS.md repo instructions are supported.",
            ],
        )

    def get_current_model(self) -> str | None:
        """Get current OpenAI model if detectable."""
        return self._detect_current_model()

    def _detect_current_model(self) -> str | None:
        """Detect current model from env."""
        model = os.environ.get("CODEX_MODEL") or os.environ.get("OPENAI_MODEL")
        if model:
            return model
        return "codex-mini"

    def get_available_models(self) -> list[str]:
        """Get available OpenAI models."""
        return self.AVAILABLE_MODELS.copy()

    def supports_dynamic_switch(self) -> bool:
        """Codex supports model switching via flags."""
        return True

    def set_model(self, model_name: str) -> bool:
        """Attempt to switch model in Codex via environment."""
        if model_name not in self.AVAILABLE_MODELS:
            return False

        # Set environment variable (affects child processes)
        os.environ["CODEX_MODEL"] = model_name

        # Also write to .codex/config.json if the directory exists
        import json
        codex_config_dir = Path.home() / ".codex"
        if codex_config_dir.exists():
            config_path = codex_config_dir / "config.json"
            try:
                config: dict = {}
                if config_path.exists():
                    config = json.loads(config_path.read_text())
                config["model"] = model_name
                config_path.write_text(json.dumps(config, indent=2))
            except (OSError, json.JSONDecodeError):
                pass

        return True

    def resolve_capability_class(self, capability: CapabilityClass) -> str | None:
        """Resolve capability class to OpenAI model."""
        return self.MODEL_MAP.get(capability)

    def apply_prompt_strategy(self, task: TaskNode) -> dict:
        """Generate Codex-specific prompt strategy."""
        model = self.resolve_capability_class(task.preferred_capability_class)
        return {
            "task_id": task.id,
            "task_type": task.type.value,
            "strategy": "model_switch",
            "target_model": model,
            "hints": [
                f"Use {model} for {task.type.value} tasks.",
                f"Codex supports switching to this model via --model flag.",
            ],
        }
