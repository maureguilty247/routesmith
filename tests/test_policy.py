"""Tests for the routing policy."""

import pytest

from routesmit.policy import (
    TASK_CAPABILITY_MAP,
    get_capability_class,
    get_task_dependencies,
    get_task_priority,
)
from routesmit.types import CapabilityClass, TaskType


class TestCapabilityMapping:
    """Test capability class mapping from task types."""

    def test_planning_maps_to_deep_reasoning(self):
        assert get_capability_class(TaskType.PLANNING) == CapabilityClass.DEEP_REASONING

    def test_analysis_maps_to_deep_reasoning(self):
        assert get_capability_class(TaskType.ANALYSIS) == CapabilityClass.DEEP_REASONING

    def test_review_maps_to_deep_reasoning(self):
        assert get_capability_class(TaskType.REVIEW) == CapabilityClass.DEEP_REASONING

    def test_coding_maps_to_coding(self):
        assert get_capability_class(TaskType.CODING) == CapabilityClass.CODING

    def test_testing_maps_to_coding(self):
        assert get_capability_class(TaskType.TESTING) == CapabilityClass.CODING

    def test_refactor_maps_to_coding(self):
        assert get_capability_class(TaskType.REFACTOR) == CapabilityClass.CODING

    def test_documentation_maps_to_balanced(self):
        assert get_capability_class(TaskType.DOCUMENTATION) == CapabilityClass.BALANCED

    def test_formatting_maps_to_fast(self):
        assert get_capability_class(TaskType.FORMATTING) == CapabilityClass.FAST

    def test_all_task_types_have_mapping(self):
        for task_type in TaskType:
            cap = get_capability_class(task_type)
            assert cap in CapabilityClass


class TestTaskDependencies:
    """Test dependency inference."""

    def test_coding_depends_on_planning(self):
        all_types = [TaskType.PLANNING, TaskType.CODING]
        deps = get_task_dependencies(TaskType.CODING, all_types)
        assert TaskType.PLANNING in deps

    def test_testing_depends_on_coding(self):
        all_types = [TaskType.CODING, TaskType.TESTING]
        deps = get_task_dependencies(TaskType.TESTING, all_types)
        assert TaskType.CODING in deps

    def test_docs_depends_on_coding(self):
        all_types = [TaskType.CODING, TaskType.DOCUMENTATION]
        deps = get_task_dependencies(TaskType.DOCUMENTATION, all_types)
        assert TaskType.CODING in deps

    def test_review_depends_on_all(self):
        all_types = [TaskType.PLANNING, TaskType.CODING, TaskType.TESTING, TaskType.REVIEW]
        deps = get_task_dependencies(TaskType.REVIEW, all_types)
        assert TaskType.PLANNING in deps
        assert TaskType.CODING in deps
        assert TaskType.TESTING in deps
        assert TaskType.REVIEW not in deps

    def test_planning_has_no_deps_alone(self):
        all_types = [TaskType.PLANNING]
        deps = get_task_dependencies(TaskType.PLANNING, all_types)
        assert deps == []

    def test_coding_no_planning_no_dep(self):
        all_types = [TaskType.CODING, TaskType.TESTING]
        deps = get_task_dependencies(TaskType.CODING, all_types)
        assert TaskType.PLANNING not in deps


class TestTaskPriority:
    """Test task priority ordering."""

    def test_planning_highest_priority(self):
        assert get_task_priority(TaskType.PLANNING) < get_task_priority(TaskType.CODING)

    def test_coding_before_testing(self):
        assert get_task_priority(TaskType.CODING) < get_task_priority(TaskType.TESTING)

    def test_review_after_coding(self):
        assert get_task_priority(TaskType.REVIEW) > get_task_priority(TaskType.CODING)
