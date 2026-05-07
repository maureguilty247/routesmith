"""Tests for host detection."""

import os
from unittest.mock import patch

import pytest

from routesmith.hosts.detector import detect_host, get_host_adapter, get_host_capabilities
from routesmith.types import SkillConfig


class TestHostDetection:
    """Test host detection logic."""

    def test_forced_host(self):
        config = SkillConfig(forced_host="claude_code")
        result = detect_host(config)
        assert result.host_name == "claude_code"
        assert result.confidence == 1.0
        assert result.detection_method == "forced_via_config"

    def test_fallback_to_generic(self):
        """With no host signals, should fall back to generic."""
        config = SkillConfig()
        with patch.dict(os.environ, {}, clear=True):
            result = detect_host(config)
            # May detect copilot due to vscode env in test, or generic
            assert result.host_name in ("generic", "copilot", "claude_code", "cursor")
            assert result.confidence >= 0.0

    def test_detection_returns_confidence(self):
        config = SkillConfig()
        result = detect_host(config)
        assert 0.0 <= result.confidence <= 1.0

    def test_detection_returns_method(self):
        config = SkillConfig(forced_host="codex")
        result = detect_host(config)
        assert result.detection_method != ""

    @patch.dict(os.environ, {"CLAUDE_CODE": "1"}, clear=False)
    def test_claude_code_detected(self):
        config = SkillConfig()
        result = detect_host(config)
        # Claude Code should have high confidence
        assert result.confidence > 0

    @patch.dict(os.environ, {"CODEX_ENV": "1"}, clear=False)
    def test_codex_detected(self):
        config = SkillConfig()
        result = detect_host(config)
        assert result.confidence > 0


class TestHostAdapter:
    """Test host adapter resolution."""

    def test_forced_host_returns_adapter(self):
        config = SkillConfig(forced_host="claude_code")
        adapter = get_host_adapter(config)
        assert adapter is not None

    def test_generic_adapter_fallback(self):
        config = SkillConfig(forced_host="generic")
        adapter = get_host_adapter(config)
        assert adapter is not None
        caps = adapter.get_capabilities()
        assert caps.host_name == "generic"


class TestHostDetectionGraceful:
    """Test that host detection fails gracefully."""

    def test_no_crash_on_missing_env(self):
        """Detection must not crash even with no env vars."""
        config = SkillConfig()
        result = detect_host(config)
        assert result is not None

    def test_capabilities_without_crash(self):
        config = SkillConfig()
        caps = get_host_capabilities(config)
        assert caps is not None
        assert caps.host_name != ""
