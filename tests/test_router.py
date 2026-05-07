"""Tests for the router."""

import pytest

from routesmith.hosts.claude_code import ClaudeCodeHostAdapter
from routesmith.hosts.copilot import CopilotHostAdapter
from routesmith.hosts.generic import GenericHostAdapter
from routesmith.planner import Planner
from routesmith.router import Router
from routesmith.types import CapabilityClass, TaskType


class TestRouterWithSwitchableHost:
    """Test router with a host that supports dynamic switching."""

    def setup_method(self):
        self.adapter = ClaudeCodeHostAdapter()
        self.router = Router(self.adapter)
        self.planner = Planner()

    def test_tasks_get_suggested_models(self):
        plan = self.planner.plan("plan and implement a feature", host_name="claude_code")
        resolved = self.router.resolve_plan(plan)

        for task in resolved.tasks:
            assert task.suggested_model is not None

    def test_planning_gets_deep_reasoning_model(self):
        plan = self.planner.plan("plan the architecture", host_name="claude_code")
        resolved = self.router.resolve_plan(plan)

        planning_tasks = [t for t in resolved.tasks if t.type == TaskType.PLANNING]
        if planning_tasks:
            expected = self.adapter.resolve_capability_class(CapabilityClass.DEEP_REASONING)
            assert planning_tasks[0].suggested_model == expected

    def test_coding_gets_coding_model(self):
        plan = self.planner.plan("implement a function", host_name="claude_code")
        resolved = self.router.resolve_plan(plan)

        coding_tasks = [t for t in resolved.tasks if t.type == TaskType.CODING]
        if coding_tasks:
            expected = self.adapter.resolve_capability_class(CapabilityClass.CODING)
            assert coding_tasks[0].suggested_model == expected

    def test_no_advisory_about_switching(self):
        plan = self.planner.plan("implement something", host_name="claude_code")
        resolved = self.router.resolve_plan(plan)

        for msg in resolved.advisory:
            assert "does not support dynamic model switching" not in msg


class TestRouterWithNonSwitchableHost:
    """Test router with a host that does NOT support dynamic switching."""

    def setup_method(self):
        self.adapter = CopilotHostAdapter()
        self.router = Router(self.adapter)
        self.planner = Planner()

    def test_tasks_have_no_suggested_model(self):
        plan = self.planner.plan("plan and implement", host_name="copilot")
        resolved = self.router.resolve_plan(plan)

        for task in resolved.tasks:
            assert task.suggested_model is None

    def test_advisory_about_no_switching(self):
        plan = self.planner.plan("implement something", host_name="copilot")
        resolved = self.router.resolve_plan(plan)

        assert any("does not support dynamic model switching" in msg for msg in resolved.advisory)

    def test_strategies_use_prompt_optimization(self):
        plan = self.planner.plan("implement and test", host_name="copilot")
        resolved = self.router.resolve_plan(plan)
        strategies = self.router.get_strategies(resolved)

        for strategy in strategies:
            assert strategy["strategy"] == "prompt_optimization"


class TestRouterWithGenericHost:
    """Test router with generic fallback host."""

    def setup_method(self):
        self.adapter = GenericHostAdapter()
        self.router = Router(self.adapter)
        self.planner = Planner()

    def test_no_model_assigned(self):
        plan = self.planner.plan("implement a feature", host_name="generic")
        resolved = self.router.resolve_plan(plan)

        for task in resolved.tasks:
            assert task.suggested_model is None

    def test_strategy_is_prompt_only(self):
        plan = self.planner.plan("implement and test", host_name="generic")
        resolved = self.router.resolve_plan(plan)
        strategies = self.router.get_strategies(resolved)

        for strategy in strategies:
            assert strategy["strategy"] == "prompt_only"

    def test_no_fake_model_switching(self):
        """Generic host must never claim models were switched."""
        plan = self.planner.plan("plan, implement, test", host_name="generic")
        resolved = self.router.resolve_plan(plan)

        for task in resolved.tasks:
            assert task.suggested_model is None
