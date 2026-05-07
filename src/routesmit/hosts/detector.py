"""Host detection logic for routesmit."""

from __future__ import annotations

import os
from pathlib import Path

from routesmit.types import HostCapabilities, HostDetectionResult, SkillConfig
from routesmit.hosts.base import BaseHostAdapter


def _get_all_adapters() -> list[BaseHostAdapter]:
    """Get all available host adapters in priority order."""
    from routesmit.hosts.claude_code import ClaudeCodeHostAdapter
    from routesmit.hosts.codex import CodexHostAdapter
    from routesmit.hosts.copilot import CopilotHostAdapter
    from routesmit.hosts.cursor import CursorHostAdapter
    from routesmit.hosts.aider import AiderHostAdapter
    from routesmit.hosts.generic import GenericHostAdapter

    return [
        ClaudeCodeHostAdapter(),
        CodexHostAdapter(),
        CopilotHostAdapter(),
        CursorHostAdapter(),
        AiderHostAdapter(),
        GenericHostAdapter(),
    ]


def detect_host(config: SkillConfig | None = None) -> HostDetectionResult:
    """Detect the current host environment."""
    if config and config.forced_host:
        return HostDetectionResult(
            host_name=config.forced_host,
            confidence=1.0,
            detection_method="forced_via_config",
            root_path=str(Path.cwd()),
        )

    adapters = _get_all_adapters()
    best: HostDetectionResult | None = None

    for adapter in adapters:
        result = adapter.detect()
        if result.confidence > 0 and (best is None or result.confidence > best.confidence):
            best = result

    if best is not None:
        return best

    return HostDetectionResult(
        host_name="generic",
        confidence=0.1,
        detection_method="fallback",
        root_path=str(Path.cwd()),
    )


def get_host_adapter(config: SkillConfig | None = None) -> BaseHostAdapter:
    """Get the adapter for the detected host."""
    detection = detect_host(config)
    adapters = _get_all_adapters()

    for adapter in adapters:
        adapter_detection = adapter.detect()
        if adapter_detection.host_name == detection.host_name:
            return adapter

    from routesmit.hosts.generic import GenericHostAdapter
    return GenericHostAdapter()


def get_host_capabilities(config: SkillConfig | None = None) -> HostCapabilities:
    """Get capabilities of the detected host."""
    adapter = get_host_adapter(config)
    return adapter.get_capabilities()
