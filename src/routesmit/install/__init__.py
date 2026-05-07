"""Install adapters for routesmit."""

from __future__ import annotations

from routesmit.install.base import BaseInstaller
from routesmit.types import InstallResult


def run_install(target: str) -> InstallResult:
    """Run install for a given target host."""
    installers: dict[str, type[BaseInstaller]] = _get_installers()

    target_lower = target.lower()
    installer_cls = installers.get(target_lower)

    if installer_cls is None:
        return InstallResult(
            target=target,
            success=False,
            warnings=[f"Unknown target: {target}. Supported: {', '.join(installers.keys())}"],
        )

    installer = installer_cls()
    return installer.install()


def _get_installers() -> dict[str, type[BaseInstaller]]:
    """Get all available installers."""
    from routesmit.install.claude import ClaudeInstaller
    from routesmit.install.codex import CodexInstaller
    from routesmit.install.copilot import CopilotInstaller
    from routesmit.install.cursor import CursorInstaller
    from routesmit.install.vscode import VSCodeInstaller
    from routesmit.install.aider import AiderInstaller
    from routesmit.install.generic import GenericInstaller

    return {
        "claude": ClaudeInstaller,
        "codex": CodexInstaller,
        "copilot": CopilotInstaller,
        "cursor": CursorInstaller,
        "vscode": VSCodeInstaller,
        "aider": AiderInstaller,
        "generic": GenericInstaller,
    }
