"""Tests for host capabilities."""

import pytest

from routesmit.hosts.claude_code import ClaudeCodeHostAdapter
from routesmit.hosts.codex import CodexHostAdapter
from routesmit.hosts.copilot import CopilotHostAdapter
from routesmit.hosts.cursor import CursorHostAdapter
from routesmit.hosts.aider import AiderHostAdapter
from routesmit.hosts.generic import GenericHostAdapter
from routesmit.types import CapabilityClass


class TestClaudeCodeCapabilities:
    """Test Claude Code host adapter."""

    def setup_method(self):
        self.adapter = ClaudeCodeHostAdapter()

    def test_model_family_is_anthropic(self):
        caps = self.adapter.get_capabilities()
        assert caps.model_family == "anthropic"

    def test_supports_dynamic_switch(self):
        assert self.adapter.supports_dynamic_switch() is True

    def test_available_models_are_claude_only(self):
        models = self.adapter.get_available_models()
        for model in models:
            assert "claude" in model.lower()

    def test_resolves_capability_classes(self):
        for cap in CapabilityClass:
            model = self.adapter.resolve_capability_class(cap)
            assert model is not None
            assert "claude" in model.lower()

    def test_set_model_known_model(self):
        assert self.adapter.set_model("claude-sonnet-4-20250514") is True

    def test_set_model_unknown_model(self):
        assert self.adapter.set_model("gpt-4") is False


class TestCodexCapabilities:
    """Test Codex host adapter."""

    def setup_method(self):
        self.adapter = CodexHostAdapter()

    def test_model_family_is_openai(self):
        caps = self.adapter.get_capabilities()
        assert caps.model_family == "openai"

    def test_supports_dynamic_switch(self):
        assert self.adapter.supports_dynamic_switch() is True

    def test_available_models_are_openai_only(self):
        models = self.adapter.get_available_models()
        # OpenAI models should not contain "claude"
        for model in models:
            assert "claude" not in model.lower()

    def test_resolves_capability_classes(self):
        for cap in CapabilityClass:
            model = self.adapter.resolve_capability_class(cap)
            assert model is not None

    def test_does_not_use_claude_models(self):
        """Codex must never suggest Claude models."""
        for cap in CapabilityClass:
            model = self.adapter.resolve_capability_class(cap)
            assert "claude" not in model.lower()


class TestCopilotCapabilities:
    """Test Copilot host adapter."""

    def setup_method(self):
        self.adapter = CopilotHostAdapter()

    def test_does_not_support_dynamic_switch(self):
        assert self.adapter.supports_dynamic_switch() is False

    def test_set_model_always_fails(self):
        assert self.adapter.set_model("any-model") is False

    def test_current_model_is_none(self):
        assert self.adapter.get_current_model() is None

    def test_prompt_strategy_used(self):
        from routesmit.types import TaskNode, TaskType
        task = TaskNode(
            id="test",
            type=TaskType.CODING,
            title="test",
            preferred_capability_class=CapabilityClass.CODING,
        )
        strategy = self.adapter.apply_prompt_strategy(task)
        assert strategy["strategy"] == "prompt_optimization"
        assert strategy["target_model"] is None


class TestGenericCapabilities:
    """Test generic host adapter."""

    def setup_method(self):
        self.adapter = GenericHostAdapter()

    def test_does_not_support_switch(self):
        assert self.adapter.supports_dynamic_switch() is False

    def test_no_models_available(self):
        assert self.adapter.get_available_models() == []

    def test_resolve_returns_none(self):
        for cap in CapabilityClass:
            assert self.adapter.resolve_capability_class(cap) is None

    def test_set_model_always_false(self):
        assert self.adapter.set_model("anything") is False

    def test_prompt_only_strategy(self):
        from routesmit.types import TaskNode, TaskType
        task = TaskNode(
            id="test",
            type=TaskType.CODING,
            title="test",
            preferred_capability_class=CapabilityClass.CODING,
        )
        strategy = self.adapter.apply_prompt_strategy(task)
        assert strategy["strategy"] == "prompt_only"


class TestCursorCapabilities:
    """Test Cursor adapter."""

    def setup_method(self):
        self.adapter = CursorHostAdapter()

    def test_does_not_support_switch(self):
        assert self.adapter.supports_dynamic_switch() is False

    def test_set_model_fails(self):
        assert self.adapter.set_model("anything") is False


class TestAiderCapabilities:
    """Test Aider adapter."""

    def setup_method(self):
        self.adapter = AiderHostAdapter()

    def test_supports_switch(self):
        assert self.adapter.supports_dynamic_switch() is True

    def test_model_family_is_mixed(self):
        caps = self.adapter.get_capabilities()
        assert caps.model_family == "mixed"
