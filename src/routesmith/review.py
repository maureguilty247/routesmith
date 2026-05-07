"""Review step for route plans."""

from __future__ import annotations

from routesmith.types import RoutePlan, RunResult, TaskResult


def review_plan(plan: RoutePlan) -> list[str]:
    """Review a route plan for potential issues.

    Returns a list of warning/advisory strings.
    """
    warnings: list[str] = []

    if not plan.tasks:
        warnings.append("Route plan has no tasks. The prompt may not have been recognized.")

    # Check for circular dependencies
    task_ids = {t.id for t in plan.tasks}
    for task in plan.tasks:
        for dep in task.dependencies:
            if dep not in task_ids:
                warnings.append(
                    f"Task '{task.id}' depends on '{dep}' which is not in the plan."
                )

    # Check for tasks without suggested models in switching-capable hosts
    if plan.host not in ("generic", "unknown"):
        tasks_without_model = [t for t in plan.tasks if t.suggested_model is None]
        if tasks_without_model and any(t.suggested_model for t in plan.tasks):
            warnings.append(
                f"{len(tasks_without_model)} task(s) have no suggested model assignment."
            )

    return warnings


def review_results(results: list[TaskResult]) -> list[str]:
    """Review execution results for issues."""
    warnings: list[str] = []

    failed = [r for r in results if not r.success]
    if failed:
        warnings.append(f"{len(failed)} task(s) failed during execution.")

    tasks_with_warnings = [r for r in results if r.warnings]
    if tasks_with_warnings:
        total_warnings = sum(len(r.warnings) for r in tasks_with_warnings)
        warnings.append(f"{total_warnings} warning(s) across {len(tasks_with_warnings)} task(s).")

    return warnings
