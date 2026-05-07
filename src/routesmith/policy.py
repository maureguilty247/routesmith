"""Routing policy - capability-first task-to-model mapping."""

from __future__ import annotations

from routesmith.types import CapabilityClass, TaskType


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
