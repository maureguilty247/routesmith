"""Tests for the planner."""

import pytest

from routesmith.planner import Planner, classify_prompt
from routesmith.types import CapabilityClass, TaskType


def _types(result: list[tuple[TaskType, float]]) -> list[TaskType]:
    """Extract just the task types from classify_prompt results."""
    return [tt for tt, _ in result]


class TestClassifyPrompt:
    """Test prompt classification."""

    def test_single_coding_task(self):
        types = _types(classify_prompt("implement a REST API"))
        assert TaskType.CODING in types

    def test_single_testing_task(self):
        types = _types(classify_prompt("write tests for the auth module"))
        assert TaskType.TESTING in types

    def test_planning_detected(self):
        types = _types(classify_prompt("plan the architecture for the new service"))
        assert TaskType.PLANNING in types

    def test_multi_task_prompt(self):
        types = _types(classify_prompt("plan this feature, implement it, add tests, and write docs"))
        assert TaskType.PLANNING in types
        assert TaskType.CODING in types
        assert TaskType.TESTING in types
        assert TaskType.DOCUMENTATION in types

    def test_refactor_detected(self):
        types = _types(classify_prompt("refactor the database layer"))
        assert TaskType.REFACTOR in types

    def test_review_detected(self):
        types = _types(classify_prompt("review the pull request"))
        assert TaskType.REVIEW in types

    def test_analysis_detected(self):
        types = _types(classify_prompt("analyze the performance bottleneck"))
        assert TaskType.ANALYSIS in types

    def test_documentation_detected(self):
        types = _types(classify_prompt("document the API endpoints"))
        assert TaskType.DOCUMENTATION in types

    def test_formatting_detected(self):
        types = _types(classify_prompt("format the code and fix linting errors"))
        assert TaskType.FORMATTING in types

    def test_unknown_defaults_to_coding(self):
        types = _types(classify_prompt("do something with the thing"))
        assert TaskType.CODING in types

    def test_confidence_scores_returned(self):
        result = classify_prompt("implement a REST API")
        assert all(0.0 < conf <= 1.0 for _, conf in result)

    def test_explicit_markers(self):
        types = _types(classify_prompt("[plan] [code] [test] build this feature"))
        assert TaskType.PLANNING in types
        assert TaskType.CODING in types
        assert TaskType.TESTING in types


class TestPlanner:
    """Test the Planner class."""

    def setup_method(self):
        self.planner = Planner()

    def test_single_task_plan(self):
        plan = self.planner.plan("implement a function")
        assert len(plan.tasks) >= 1
        assert plan.original_prompt == "implement a function"
        assert "Single-task" in plan.rationale or len(plan.tasks) == 1

    def test_multi_task_plan(self):
        plan = self.planner.plan("plan, implement, test, and document a feature")
        assert len(plan.tasks) >= 3

    def test_tasks_have_ids(self):
        plan = self.planner.plan("plan and implement a feature")
        for task in plan.tasks:
            assert task.id is not None
            assert len(task.id) > 0

    def test_tasks_have_capability_classes(self):
        plan = self.planner.plan("plan, code, and review")
        for task in plan.tasks:
            assert task.preferred_capability_class in CapabilityClass

    def test_dependency_ordering(self):
        plan = self.planner.plan("plan the feature and then implement it")
        # Find planning and coding tasks
        planning_tasks = [t for t in plan.tasks if t.type == TaskType.PLANNING]
        coding_tasks = [t for t in plan.tasks if t.type == TaskType.CODING]
        if planning_tasks and coding_tasks:
            assert planning_tasks[0].id in coding_tasks[0].dependencies

    def test_plan_mode_is_auto(self):
        plan = self.planner.plan("do something")
        assert plan.mode == "auto"

    def test_plan_has_rationale(self):
        plan = self.planner.plan("implement and test")
        assert plan.rationale != ""

    def test_host_name_passed_through(self):
        plan = self.planner.plan("implement something", host_name="claude_code")
        assert plan.host == "claude_code"

    def test_planner_works_without_api_keys(self):
        """Planner must be fully deterministic and offline."""
        plan = self.planner.plan("plan, implement, test, and document everything")
        assert plan is not None
        assert len(plan.tasks) > 0
