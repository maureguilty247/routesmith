"""Tests for the CLI."""

import pytest
from typer.testing import CliRunner

from routesmith.cli import app

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "routesmith" in result.output.lower() or "host-aware" in result.output.lower()

    def test_explain_command(self):
        result = runner.invoke(app, ["explain", "plan and implement a feature"])
        assert result.exit_code == 0
        assert "Route Plan" in result.output or "planning" in result.output.lower()

    def test_detect_host_command(self):
        result = runner.invoke(app, ["detect-host"])
        assert result.exit_code == 0
        assert "Host" in result.output

    def test_capabilities_command(self):
        result = runner.invoke(app, ["capabilities"])
        assert result.exit_code == 0
        assert "Capabilities" in result.output or "Model Family" in result.output

    def test_doctor_command(self):
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "routesmith" in result.output

    def test_run_command(self):
        result = runner.invoke(app, ["run", "implement a function"])
        assert result.exit_code == 0
        assert "Route Summary" in result.output or "Task Results" in result.output

    def test_run_with_model_pin(self):
        result = runner.invoke(app, ["run", "implement something", "--model", "test-model"])
        assert result.exit_code == 0
        # Should show pinned model advisory
        assert "Pinned" in result.output or "model" in result.output.lower()

    def test_explain_multi_task(self):
        result = runner.invoke(app, ["explain", "plan, implement, test, and document"])
        assert result.exit_code == 0
        # Should show multiple tasks
        assert "planning" in result.output.lower() or "coding" in result.output.lower()
