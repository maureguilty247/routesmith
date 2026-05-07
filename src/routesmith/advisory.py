"""Advisory messages for routesmith."""

from __future__ import annotations

from routesmith.types import HostCapabilities, RoutePlan


PINNED_MODEL_ADVISORY = (
    "Pinned model execution is active. Auto mode is recommended for mixed tasks "
    "because routesmith can decompose planning, coding, testing, and documentation "
    "into separate steps and use the best available host-compatible model where supported."
)

NO_SWITCH_ADVISORY = (
    "This host does not support dynamic model switching. "
    "routesmith will optimize prompts and decompose tasks, but cannot change models."
)

SINGLE_TASK_ADVISORY = (
    "Single-task prompt detected. No multi-step decomposition needed."
)


def generate_advisory(
    plan: RoutePlan,
    capabilities: HostCapabilities,
    pinned_model: str | None = None,
) -> list[str]:
    """Generate advisory messages based on plan and host capabilities."""
    messages: list[str] = []

    if pinned_model:
        messages.append(PINNED_MODEL_ADVISORY)

    if not capabilities.supports_dynamic_switch:
        messages.append(NO_SWITCH_ADVISORY)

    if len(plan.tasks) == 1:
        messages.append(SINGLE_TASK_ADVISORY)

    if len(plan.tasks) > 3 and not capabilities.supports_dynamic_switch:
        messages.append(
            f"Complex multi-step task ({len(plan.tasks)} steps) detected in a host "
            f"without model switching. Each step will use optimized prompts."
        )

    return messages
