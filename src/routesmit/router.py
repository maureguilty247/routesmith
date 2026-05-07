"""Router - resolves task nodes to host-compatible models or strategies."""

from __future__ import annotations

from routesmit.hosts.base import BaseHostAdapter
from routesmit.types import RoutePlan, TaskNode


class Router:
    """Routes tasks to models or prompt strategies based on host capabilities."""

    def __init__(self, adapter: BaseHostAdapter) -> None:
        self.adapter = adapter

    def resolve_plan(self, plan: RoutePlan) -> RoutePlan:
        """Resolve each task in the plan to a concrete model or strategy.

        If the host supports dynamic switching, tasks get a suggested_model.
        If not, tasks still get capability class annotations but no fake model assignment.
        """
        can_switch = self.adapter.supports_dynamic_switch()

        for task in plan.tasks:
            if can_switch:
                model = self.adapter.resolve_capability_class(task.preferred_capability_class)
                task.suggested_model = model
            else:
                # Cannot switch - leave suggested_model as None
                task.suggested_model = None

        # Add advisory about switching capability
        if not can_switch:
            plan.advisory.append(
                "Host does not support dynamic model switching. "
                "Task decomposition and prompt optimization will be applied instead."
            )

        return plan

    def get_task_strategy(self, task: TaskNode) -> dict:
        """Get the execution strategy for a single task."""
        return self.adapter.apply_prompt_strategy(task)

    def get_strategies(self, plan: RoutePlan) -> list[dict]:
        """Get strategies for all tasks in a plan."""
        return [self.get_task_strategy(task) for task in plan.tasks]
