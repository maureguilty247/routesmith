"""routesmit - Host-aware auto-routing skill library for IDEs and coding agents."""

from routesmit.types import (
    CapabilityClass,
    HostCapabilities,
    HostDetectionResult,
    InstallResult,
    RoutePlan,
    RunResult,
    SkillConfig,
    TaskNode,
    TaskResult,
    TaskType,
)
from routesmit.executor import Executor
from routesmit.planner import Planner
from routesmit.router import Router
from routesmit.hosts.detector import detect_host, get_host_capabilities

__version__ = "0.1.0"
__all__ = [
    "run",
    "explain_route",
    "detect_host",
    "get_host_capabilities",
    "serve_stdio",
    "install",
    "CapabilityClass",
    "HostCapabilities",
    "HostDetectionResult",
    "InstallResult",
    "RoutePlan",
    "RunResult",
    "SkillConfig",
    "TaskNode",
    "TaskResult",
    "TaskType",
    "Executor",
    "Planner",
    "Router",
]


def run(
    prompt: str,
    mode: str = "auto",
    model: str | None = None,
    config: SkillConfig | None = None,
) -> RunResult:
    """Execute a prompt through routesmit's host-aware routing pipeline."""
    executor = Executor(config=config)
    return executor.run(prompt, mode=mode, model=model)


def explain_route(
    prompt: str,
    config: SkillConfig | None = None,
) -> RoutePlan:
    """Explain the route plan for a prompt without executing."""
    executor = Executor(config=config)
    return executor.explain(prompt)


def serve_stdio() -> None:
    """Start the stdio server for tool integration."""
    from routesmit.server.stdio import run_stdio_server
    run_stdio_server()


def install(target: str) -> InstallResult:
    """Install routesmit configuration for a target host."""
    from routesmit.install import run_install
    return run_install(target)
