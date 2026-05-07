"""Tests for advisory messages."""

import pytest

from routesmith.advisory import (
    NO_SWITCH_ADVISORY,
    PINNED_MODEL_ADVISORY,
    SINGLE_TASK_ADVISORY,
    generate_advisory,
)
from routesmith.planner import Planner
from routesmith.types import HostCapabilities, RoutePlan, TaskNode, TaskType, CapabilityClass


def _make_capabilities(supports_switch: bool = False) -> HostCapabilities:
    return HostCapabilities(
        host_name="test",
        detected=True,
        supports_dynamic_switch=supports_switch,
        model_family="test",
    )


def _make_plan(num_tasks: int = 1) -> RoutePlan:
    tasks = [
        TaskNode(
            id=f"task_{i}",
            type=TaskType.CODING,
            title=f"Task {i}",
            preferred_capability_class=CapabilityClass.CODING,
        )
        for i in range(num_tasks)
    ]
    return RoutePlan(original_prompt="test", tasks=tasks)


class TestAdvisory:
    """Test advisory message generation."""

    def test_pinned_model_advisory(self):
        plan = _make_plan(2)
        caps = _make_capabilities(supports_switch=True)
        messages = generate_advisory(plan, caps, pinned_model="some-model")
        assert PINNED_MODEL_ADVISORY in messages

    def test_no_pinned_model_no_advisory(self):
        plan = _make_plan(2)
        caps = _make_capabilities(supports_switch=True)
        messages = generate_advisory(plan, caps, pinned_model=None)
        assert PINNED_MODEL_ADVISORY not in messages

    def test_no_switch_advisory(self):
        plan = _make_plan(2)
        caps = _make_capabilities(supports_switch=False)
        messages = generate_advisory(plan, caps)
        assert NO_SWITCH_ADVISORY in messages

    def test_switch_supported_no_advisory(self):
        plan = _make_plan(2)
        caps = _make_capabilities(supports_switch=True)
        messages = generate_advisory(plan, caps)
        assert NO_SWITCH_ADVISORY not in messages

    def test_single_task_advisory(self):
        plan = _make_plan(1)
        caps = _make_capabilities(supports_switch=True)
        messages = generate_advisory(plan, caps)
        assert SINGLE_TASK_ADVISORY in messages

    def test_complex_task_no_switch_advisory(self):
        plan = _make_plan(5)
        caps = _make_capabilities(supports_switch=False)
        messages = generate_advisory(plan, caps)
        assert any("Complex multi-step" in msg for msg in messages)
