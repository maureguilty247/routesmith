"""Custom exceptions for routesmit."""


class RouterSmitError(Exception):
    """Base exception for routesmit."""


class HostDetectionError(RouterSmitError):
    """Raised when host detection fails critically."""


class ModelSwitchError(RouterSmitError):
    """Raised when a model switch attempt fails."""


class PlannerError(RouterSmitError):
    """Raised when the planner cannot decompose a prompt."""


class PolicyError(RouterSmitError):
    """Raised when policy resolution fails."""


class ExecutionError(RouterSmitError):
    """Raised when task execution fails."""


class ConfigurationError(RouterSmitError):
    """Raised when configuration is invalid."""


class InstallError(RouterSmitError):
    """Raised when an install operation fails."""


class ProviderError(RouterSmitError):
    """Raised when a provider operation fails."""
