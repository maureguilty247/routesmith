"""Routing policy - capability-first task-to-model mapping."""

from __future__ import annotations

from routesmith.types import CapabilityClass, RoutingPreference, TaskType


# Maps task types to their preferred capability class
TASK_CAPABILITY_MAP: dict[TaskType, CapabilityClass] = {
    TaskType.PLANNING: CapabilityClass.DEEP_REASONING,
    TaskType.ANALYSIS: CapabilityClass.DEEP_REASONING,
    TaskType.REVIEW: CapabilityClass.DEEP_REASONING,
    TaskType.CODING: CapabilityClass.CODING,
    TaskType.TESTING: CapabilityClass.CODING,
    TaskType.REFACTOR: CapabilityClass.CODING,
    TaskType.DOCUMENTATION: CapabilityClass.BALANCED,
    TaskType.FORMATTING: CapabilityClass.FAST,
}


def get_capability_class(task_type: TaskType) -> CapabilityClass:
    """Get the preferred capability class for a task type."""
    return TASK_CAPABILITY_MAP.get(task_type, CapabilityClass.BALANCED)


def _normalize_override_token(value: str) -> str:
    """Normalize config tokens so TOML overrides are forgiving."""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _normalize_routing_preference(value: RoutingPreference | str) -> RoutingPreference:
    """Normalize user-provided routing preferences into the enum."""
    if isinstance(value, RoutingPreference):
        return value
    normalized = _normalize_override_token(value)
    try:
        return RoutingPreference(normalized)
    except ValueError:
        return RoutingPreference.BALANCED


def _parse_capability_override(value: str) -> CapabilityClass | None:
    """Parse a capability override value into an enum if valid."""
    normalized = _normalize_override_token(value)
    try:
        return CapabilityClass(normalized)
    except ValueError:
        return None


def _lookup_override(policy_overrides: dict[str, str], key: str) -> str | None:
    """Look up a policy override by normalized key."""
    normalized_key = _normalize_override_token(key)
    for override_key, override_value in policy_overrides.items():
        if _normalize_override_token(str(override_key)) == normalized_key:
            return str(override_value)
    return None


def apply_policy_override(
    task_type: TaskType,
    preferred_capability: CapabilityClass,
    policy_overrides: dict[str, str] | None = None,
) -> tuple[CapabilityClass, list[str]]:
    """Apply config-driven policy overrides to a task capability.

    Supports two override styles:
    - task-type specific: planning = "balanced"
    - capability remap: deep_reasoning = "coding"
    """
    if not policy_overrides:
        return preferred_capability, []

    valid_values = ", ".join(cap.value for cap in CapabilityClass)

    task_override = _lookup_override(policy_overrides, task_type.value)
    if task_override is not None:
        override_capability = _parse_capability_override(task_override)
        if override_capability is None:
            return preferred_capability, [
                f"Ignored invalid policy override for {task_type.value}: {task_override!r}. "
                f"Expected one of: {valid_values}."
            ]
        if override_capability != preferred_capability:
            return override_capability, [
                f"Applied policy override for {task_type.value}: "
                f"{preferred_capability.value} -> {override_capability.value}."
            ]
        return preferred_capability, []

    capability_override = _lookup_override(policy_overrides, preferred_capability.value)
    if capability_override is not None:
        override_capability = _parse_capability_override(capability_override)
        if override_capability is None:
            return preferred_capability, [
                f"Ignored invalid capability override for {preferred_capability.value}: "
                f"{capability_override!r}. Expected one of: {valid_values}."
            ]
        if override_capability != preferred_capability:
            return override_capability, [
                f"Applied capability override for {preferred_capability.value}: "
                f"{preferred_capability.value} -> {override_capability.value}."
            ]

    return preferred_capability, []


def apply_routing_preference(
    task_type: TaskType,
    preferred_capability: CapabilityClass,
    routing_preference: RoutingPreference | str,
) -> tuple[CapabilityClass, list[str]]:
    """Apply built-in cost-aware or quality-first routing preferences."""
    preference = _normalize_routing_preference(routing_preference)
    if preference == RoutingPreference.BALANCED:
        return preferred_capability, []

    if preference == RoutingPreference.COST:
        remap = {
            CapabilityClass.DEEP_REASONING: CapabilityClass.BALANCED,
            CapabilityClass.CODING: CapabilityClass.BALANCED,
            CapabilityClass.BALANCED: CapabilityClass.FAST,
            CapabilityClass.FAST: CapabilityClass.FAST,
        }
        label = "cost-aware"
    else:
        remap = {
            CapabilityClass.DEEP_REASONING: CapabilityClass.DEEP_REASONING,
            CapabilityClass.CODING: CapabilityClass.DEEP_REASONING,
            CapabilityClass.BALANCED: CapabilityClass.CODING,
            CapabilityClass.FAST: CapabilityClass.BALANCED,
        }
        label = "quality-first"

    resolved = remap.get(preferred_capability, preferred_capability)
    if resolved == preferred_capability:
        return preferred_capability, []

    return resolved, [
        f"Applied {label} routing for {task_type.value}: "
        f"{preferred_capability.value} -> {resolved.value}."
    ]


def get_task_priority(task_type: TaskType) -> int:
    """Get default priority for a task type (lower = higher priority)."""
    priority_map: dict[TaskType, int] = {
        TaskType.PLANNING: 1,
        TaskType.ANALYSIS: 2,
        TaskType.CODING: 3,
        TaskType.TESTING: 4,
        TaskType.REFACTOR: 5,
        TaskType.DOCUMENTATION: 6,
        TaskType.REVIEW: 7,
        TaskType.FORMATTING: 8,
    }
    return priority_map.get(task_type, 5)


def get_task_dependencies(task_type: TaskType, all_types: list[TaskType]) -> list[TaskType]:
    """Infer dependencies for a task type given the full set of tasks.

    Rules:
    - planning before coding
    - coding before testing
    - coding before docs (if docs depend on implementation)
    - all meaningful tasks before final review
    """
    deps: list[TaskType] = []

    if task_type == TaskType.CODING and TaskType.PLANNING in all_types:
        deps.append(TaskType.PLANNING)
    if task_type == TaskType.CODING and TaskType.ANALYSIS in all_types:
        deps.append(TaskType.ANALYSIS)

    if task_type == TaskType.TESTING and TaskType.CODING in all_types:
        deps.append(TaskType.CODING)

    if task_type == TaskType.DOCUMENTATION and TaskType.CODING in all_types:
        deps.append(TaskType.CODING)

    if task_type == TaskType.REFACTOR and TaskType.CODING in all_types:
        deps.append(TaskType.CODING)

    if task_type == TaskType.REVIEW:
        # Review depends on all other present tasks
        for t in all_types:
            if t != TaskType.REVIEW:
                deps.append(t)

    if task_type == TaskType.FORMATTING:
        # Formatting after coding and docs
        if TaskType.CODING in all_types:
            deps.append(TaskType.CODING)
        if TaskType.DOCUMENTATION in all_types:
            deps.append(TaskType.DOCUMENTATION)

    return deps
