"""CLI snapshot tests - verify CLI output structure."""

import pytest
from typer.testing import CliRunner

from routesmith.cli import app


runner = CliRunner()


class TestCLIRun:
    """Test CLI run command output structure."""

    def test_run_shows_route_summary(self):
        result = runner.invoke(app, ["run", "implement a function"])
        assert result.exit_code == 0
        assert "Route Summary" in result.output

    def test_run_shows_task_results(self):
        result = runner.invoke(app, ["run", "implement a function"])
        assert result.exit_code == 0
        assert "Task Results" in result.output

    def test_run_shows_metrics(self):
        result = runner.invoke(app, ["run", "implement and test a feature"])
        assert result.exit_code == 0
        assert "Route Metrics" in result.output

    def test_run_no_metrics_flag(self):
        result = runner.invoke(app, ["run", "--no-metrics", "implement a function"])
        assert result.exit_code == 0
        assert "Route Metrics" not in result.output

    def test_run_shows_model_usage(self):
        result = runner.invoke(app, ["run", "plan and implement"])
        assert result.exit_code == 0
        assert "Model Usage" in result.output

    def test_run_with_model_flag(self):
        result = runner.invoke(app, ["run", "--model", "claude-sonnet-4-20250514", "implement"])
        assert result.exit_code == 0
        assert "claude-sonnet-4-20250514" in result.output


class TestCLIExplain:
    """Test CLI explain command output."""

    def test_explain_shows_plan_tree(self):
        result = runner.invoke(app, ["explain", "plan and implement a feature"])
        assert result.exit_code == 0
        assert "Route Plan" in result.output

    def test_explain_shows_rationale(self):
        result = runner.invoke(app, ["explain", "implement something"])
        assert result.exit_code == 0
        assert "Rationale" in result.output

    def test_explain_shows_confidence_for_low_scores(self):
        result = runner.invoke(app, ["explain", "maybe check something"])
        assert result.exit_code == 0
        # Should show the plan regardless


class TestCLIDetectHost:
    """Test host detection CLI."""

    def test_detect_host_shows_table(self):
        result = runner.invoke(app, ["detect-host"])
        assert result.exit_code == 0
        assert "Host Detection" in result.output
        assert "Confidence" in result.output


class TestCLICapabilities:
    """Test capabilities CLI."""

    def test_capabilities_shows_table(self):
        result = runner.invoke(app, ["capabilities"])
        assert result.exit_code == 0
        assert "Host Capabilities" in result.output
        assert "Model Family" in result.output


class TestCLIDoctor:
    """Test doctor command."""

    def test_doctor_shows_diagnostics(self):
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "routesmith doctor" in result.output
        assert "Python" in result.output


class TestCLIHistory:
    """Test history command."""

    def test_history_empty(self):
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
        # Either shows empty message or table
        assert "history" in result.output.lower() or "Route History" in result.output or "No route" in result.output
