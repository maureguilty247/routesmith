"""Tests for the executor."""

import pytest

from routesmith.executor import Executor
from routesmith.types import SkillConfig


class TestExecutor:
    """Test the executor pipeline."""

    def setup_method(self):
        self.config = SkillConfig(forced_host="generic")
        self.executor = Executor(config=self.config)

    def test_run_returns_result(self):
        result = self.executor.run("implement a function")
        assert result is not None
        assert result.host == "generic"
        assert len(result.tasks) > 0

    def test_run_auto_mode(self):
        result = self.executor.run("plan and implement a feature")
        assert result.raw_plan is not None
        assert result.raw_plan.mode == "auto"

    def test_run_with_pinned_model(self):
        result = self.executor.run("implement something", model="custom-model")
        # Should have advisory about pinned model
        assert any("Pinned model" in msg for msg in result.advisory)

    def test_explain_returns_plan(self):
        plan = self.executor.explain("plan, implement, and test")
        assert plan is not None
        assert len(plan.tasks) >= 2
        assert plan.original_prompt == "plan, implement, and test"

    def test_route_summary_generated(self):
        result = self.executor.run("implement and test a feature")
        assert result.route_summary != ""
        assert "Host:" in result.route_summary

    def test_no_fake_switching_in_generic(self):
        """Generic host must not claim switching happened."""
        result = self.executor.run("plan and implement")
        for task in result.tasks:
            if task.warnings:
                assert any("not available" in w or "prompt strategy" in w for w in task.warnings)

    def test_works_without_api_keys(self):
        """Executor must work without external API keys."""
        result = self.executor.run("implement, test, and document a feature")
        assert result is not None
        assert result.final_output != ""

    def test_multi_task_creates_multiple_results(self):
        result = self.executor.run("plan, code, test, review")
        assert len(result.tasks) >= 3
