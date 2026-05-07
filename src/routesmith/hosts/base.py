"""Base host adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from routesmith.types import (
    CapabilityClass,
    HostCapabilities,
    HostDetectionResult,
    RoutePlan,
    TaskNode,
)


class BaseHostAdapter(ABC):
    """Abstract base class for host adapters."""

    @abstractmethod
    def detect(self) -> HostDetectionResult:
        """Detect whether this host is active."""
        ...

    @abstractmethod
    def get_capabilities(self) -> HostCapabilities:
        """Get the capabilities of this host."""
        ...

    @abstractmethod
    def get_current_model(self) -> str | None:
        """Get the currently active model, if detectable."""
        ...

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of models available in this host."""
        ...

    @abstractmethod
    def supports_dynamic_switch(self) -> bool:
        """Whether this host supports dynamic model switching."""
        ...

    @abstractmethod
    def set_model(self, model_name: str) -> bool:
        """Attempt to switch the active model. Returns True if successful."""
        ...

    @abstractmethod
    def resolve_capability_class(self, capability: CapabilityClass) -> str | None:
        """Resolve a capability class to the best available model name."""
        ...

    def apply_prompt_strategy(self, task: TaskNode) -> dict:
        """Generate prompt strategy hints for a task when model switching is unavailable."""
        return {
            "task_id": task.id,
            "task_type": task.type.value,
            "strategy": "default",
            "hints": [
                f"Focus on {task.type.value} for this step.",
                f"Task: {task.title}",
            ],
        }

    def apply_repo_instructions(self, route_plan: RoutePlan) -> None:
        """Apply repo-level instructions if supported. No-op by default."""
        pass
