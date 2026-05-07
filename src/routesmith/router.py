"""Router - resolves task nodes to host-compatible models or strategies."""

from __future__ import annotations

from routesmith.hosts.base import BaseHostAdapter
from routesmith.policy import apply_policy_override, apply_routing_preference
from routesmith.policy_plugins import (
    PolicyPluginContext,
    load_policy_plugins,
    normalize_plugin_result,
)
from routesmith.types import CapabilityClass, RoutePlan, RoutingPreference, SkillConfig, TaskNode


class Router:
    """Routes tasks to models or prompt strategies based on host capabilities."""

    def __init__(
        self,
        adapter: BaseHostAdapter,
        config: SkillConfig | None = None,
        policy_overrides: dict[str, str] | None = None,
        routing_preference: RoutingPreference | str | None = None,
        policy_plugins: list[str] | None = None,
    ) -> None:
        self.adapter = adapter
        self.config = config
        self.policy_overrides = policy_overrides or (config.policy_overrides if config else {})
        self.routing_preference = routing_preference if routing_preference is not None else (
            config.routing_preference if config else RoutingPreference.BALANCED
        )
        plugin_specs = policy_plugins if policy_plugins is not None else (
            config.policy_plugins if config else []
        )
        self.policy_plugins, self.plugin_warnings = load_policy_plugins(plugin_specs)

    def resolve_plan(self, plan: RoutePlan) -> RoutePlan:
        """Resolve each task in the plan to a concrete model or strategy.

        If the host supports dynamic switching, tasks get a suggested_model.
        If not, tasks still get capability class annotations but no fake model assignment.
        """
        can_switch = self.adapter.supports_dynamic_switch()
        capabilities = self.adapter.get_capabilities()
        available_models = set(self.adapter.get_available_models())
        extra_advisory: list[str] = []

        for warning in self.plugin_warnings:
            if warning not in plan.advisory and warning not in extra_advisory:
                extra_advisory.append(warning)

        for task in plan.tasks:
            resolved_capability, messages = apply_policy_override(
                task.type,
                task.preferred_capability_class,
                self.policy_overrides,
            )

            routed_capability, preference_messages = apply_routing_preference(
                task.type,
                resolved_capability,
                self.routing_preference,
            )

            suggested_model = None
            if can_switch:
                suggested_model = self.adapter.resolve_model_for_capability(
                    routed_capability,
                    self.routing_preference,
                )

            routed_capability, suggested_model, plugin_messages = self._apply_policy_plugins(
                plan,
                task,
                capabilities,
                available_models,
                routed_capability,
                suggested_model,
                can_switch,
            )

            task.preferred_capability_class = routed_capability

            for message in messages + preference_messages + plugin_messages:
                if message not in plan.advisory and message not in extra_advisory:
                    extra_advisory.append(message)

            if can_switch:
                task.suggested_model = suggested_model
            else:
                # Cannot switch - leave suggested_model as None
                task.suggested_model = None

        plan.advisory.extend(extra_advisory)

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

    def _apply_policy_plugins(
        self,
        plan: RoutePlan,
        task: TaskNode,
        capabilities,
        available_models: set[str],
        preferred_capability_class: CapabilityClass,
        suggested_model: str | None,
        can_switch: bool,
    ) -> tuple[CapabilityClass, str | None, list[str]]:
        """Run Python policy plugins on the routed task."""
        messages: list[str] = []
        capability = preferred_capability_class
        model = suggested_model

        for plugin in self.policy_plugins:
            context = PolicyPluginContext(
                task=task,
                plan=plan,
                adapter=self.adapter,
                capabilities=capabilities,
                config=self.config,
                routing_preference=str(getattr(self.routing_preference, "value", self.routing_preference)),
                preferred_capability_class=capability,
                suggested_model=model,
            )
            raw_result = plugin.handler(context)
            result, warnings = normalize_plugin_result(raw_result, plugin.name)
            messages.extend(warnings)

            if result.preferred_capability_class is not None:
                capability = result.preferred_capability_class
                if can_switch and result.suggested_model is None:
                    model = self.adapter.resolve_model_for_capability(
                        capability,
                        self.routing_preference,
                    )

            if result.suggested_model is not None:
                if not can_switch:
                    messages.append(
                        f"Policy plugin {plugin.name} suggested model {result.suggested_model}, "
                        "but the host does not support dynamic switching."
                    )
                elif result.suggested_model not in available_models:
                    messages.append(
                        f"Policy plugin {plugin.name} suggested unavailable model "
                        f"{result.suggested_model}."
                    )
                else:
                    model = result.suggested_model

            messages.extend(f"[{plugin.name}] {note}" for note in result.advisory)

        return capability, model, messages
