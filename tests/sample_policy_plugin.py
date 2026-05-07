"""Sample policy plugins used by the routesmith test suite."""

from __future__ import annotations

from routesmith.policy_plugins import BasePolicyPlugin, PolicyPluginResult
from routesmith.types import CapabilityClass, TaskType


class PreferBalancedPlanningPlugin(BasePolicyPlugin):
    """Downgrade planning to balanced capability for test coverage."""

    name = "prefer_balanced_planning"

    def apply(self, context):
        if context.task.type == TaskType.PLANNING:
            return PolicyPluginResult(
                preferred_capability_class=CapabilityClass.BALANCED,
                advisory=["Balanced planning plugin applied."],
            )
        return None


class PreferFastClaudeCodingPlugin(BasePolicyPlugin):
    """Force a cheap explicit model on Claude coding tasks for test coverage."""

    name = "prefer_fast_claude_coding"

    def apply(self, context):
        if context.task.type == TaskType.CODING:
            return PolicyPluginResult(
                suggested_model="claude-haiku-4-5",
                advisory=["Forced low-cost coding model."],
            )
        return None