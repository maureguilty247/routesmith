"""Configuration loading for routesmith."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from routesmith.types import SkillConfig


def _find_config_file() -> Path | None:
    """Find .routesmith.toml in CWD or parents."""
    cwd = Path.cwd()
    for directory in [cwd, *cwd.parents]:
        config_path = directory / ".routesmith.toml"
        if config_path.exists():
            return config_path
        if directory == Path.home():
            break
    return None


def _parse_toml(path: Path) -> dict[str, Any]:
    """Parse a TOML file."""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            return _parse_toml_fallback(path)

    with open(path, "rb") as f:
        data = tomllib.load(f)
    return data.get("routesmith", data)


def _parse_toml_fallback(path: Path) -> dict[str, Any]:
    """Minimal TOML parser for simple key = value files."""
    result: dict[str, Any] = {}
    in_section = False
    for line in path.read_text().splitlines():
        line = line.strip()
        if line == "[routesmith]":
            in_section = True
            continue
        if line.startswith("["):
            in_section = False
            continue
        if not in_section or not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.lower() in ("true", "false"):
                result[key] = value.lower() == "true"
            elif value.isdigit():
                result[key] = int(value)
            else:
                result[key] = value
    return result


def load_config() -> SkillConfig:
    """Load configuration from .routesmith.toml + environment variables.

    Priority: env vars > config file > defaults.
    """
    file_config: dict[str, Any] = {}
    config_file: str | None = None

    config_path = _find_config_file()
    if config_path:
        file_config = _parse_toml(config_path)
        config_file = str(config_path)

    def _get(key: str, env_var: str, default: Any, cast: type = str) -> Any:
        env_val = os.environ.get(env_var)
        if env_val is not None:
            if cast == bool:
                return env_val.lower() in ("true", "1", "yes")
            return cast(env_val)
        if key in file_config:
            return file_config[key]
        return default

    return SkillConfig(
        default_mode=_get("default_mode", "ROUTESMITH_DEFAULT_MODE", "auto"),
        allow_model_switch=_get("allow_model_switch", "ROUTESMITH_ALLOW_MODEL_SWITCH", True, bool),
        debug=_get("debug", "ROUTESMITH_DEBUG", False, bool),
        telemetry_enabled=_get("telemetry_enabled", "ROUTESMITH_ENABLE_TELEMETRY", False, bool),
        forced_host=_get("forced_host", "ROUTESMITH_FORCE_HOST", None) or None,
        default_host=_get("default_host", "ROUTESMITH_DEFAULT_HOST", None) or None,
        show_metrics=_get("show_metrics", "ROUTESMITH_SHOW_METRICS", True, bool),
        save_routes=_get("save_routes", "ROUTESMITH_SAVE_ROUTES", False, bool),
        routes_dir=_get("routes_dir", "ROUTESMITH_ROUTES_DIR", ".routesmith/routes"),
        config_file=config_file,
        policy_overrides=file_config.get("policy_overrides", {}),
    )
