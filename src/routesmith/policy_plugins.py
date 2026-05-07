"""Python policy plugin loading and execution for routesmith."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Callable

from routesmith.hosts.base import BaseHostAdapter
from routesmith.types import CapabilityClass, HostCapabilities, RoutePlan, SkillConfig, TaskNode


@dataclass(slots=True)
class PolicyPluginContext:
    """Context passed to Python policy plugins."""

    task: TaskNode
    plan: RoutePlan
    adapter: BaseHostAdapter
    capabilities: HostCapabilities
    config: SkillConfig | None
    routing_preference: str
    preferred_capability_class: CapabilityClass
    suggested_model: str | None = None


@dataclass(slots=True)
class PolicyPluginResult:
    """Result returned by a Python policy plugin."""

    preferred_capability_class: CapabilityClass | None = None
    suggested_model: str | None = None
    advisory: list[str] = field(default_factory=list)


class BasePolicyPlugin:
    """Base class for Python policy plugins."""

    name = "base_policy_plugin"

    def apply(self, context: PolicyPluginContext) -> PolicyPluginResult | dict[str, Any] | None:
        raise NotImplementedError


@dataclass(slots=True)
class LoadedPolicyPlugin:
    """Resolved plugin callable plus display name."""

    name: str
    handler: Callable[[PolicyPluginContext], PolicyPluginResult | dict[str, Any] | None]


def _coerce_capability(value: Any) -> CapabilityClass | None:
    if value is None:
        return None
    if isinstance(value, CapabilityClass):
        return value
    normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    try:
        return CapabilityClass(normalized)
    except ValueError:
        return None


def normalize_plugin_result(
    result: PolicyPluginResult | dict[str, Any] | None,
    plugin_name: str,
) -> tuple[PolicyPluginResult, list[str]]:
    """Normalize plugin output into a consistent dataclass."""
    if result is None:
        return PolicyPluginResult(), []

    if isinstance(result, PolicyPluginResult):
        return result, []

    if not isinstance(result, dict):
        return PolicyPluginResult(), [
            f"Policy plugin {plugin_name} returned an unsupported result type: "
            f"{type(result).__name__}."
        ]

    capability = result.get("preferred_capability_class", result.get("capability_class"))
    normalized_capability = _coerce_capability(capability)
    warnings: list[str] = []
    if capability is not None and normalized_capability is None:
        warnings.append(
            f"Policy plugin {plugin_name} returned invalid capability override: {capability!r}."
        )

    advisory = result.get("advisory", [])
    if isinstance(advisory, str):
        advisory = [advisory]
    elif not isinstance(advisory, list):
        advisory = [str(advisory)]

    return (
        PolicyPluginResult(
            preferred_capability_class=normalized_capability,
            suggested_model=result.get("suggested_model"),
            advisory=[str(item) for item in advisory],
        ),
        warnings,
    )


def load_policy_plugins(specs: list[str] | None) -> tuple[list[LoadedPolicyPlugin], list[str]]:
    """Load Python policy plugins from module specs like ``pkg.module:plugin``."""
    plugins: list[LoadedPolicyPlugin] = []
    warnings: list[str] = []

    for raw_spec in specs or []:
        spec = raw_spec.strip()
        if not spec:
            continue

        module_name, separator, object_name = spec.partition(":")
        target_name = object_name or "plugin"

        try:
            module = import_module(module_name)
            target = getattr(module, target_name)
            if isinstance(target, type):
                target = target()

            if hasattr(target, "apply") and callable(target.apply):
                handler = target.apply
                name = getattr(target, "name", spec)
            elif callable(target):
                handler = target
                name = getattr(target, "__name__", spec)
            else:
                raise TypeError("Plugin target must be callable or expose an apply() method")

            plugins.append(LoadedPolicyPlugin(name=str(name), handler=handler))
        except Exception as exc:
            suffix = "" if separator else ":plugin"
            warnings.append(
                f"Failed to load policy plugin {spec or module_name + suffix}: {exc}."
            )

    return plugins, warnings