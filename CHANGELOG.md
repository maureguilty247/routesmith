# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-05-07

### Added
- Host-aware auto-routing with capability-first model selection
- Host adapters: Claude Code, Codex, Copilot, Cursor, Aider, Generic
- Deterministic task planner with weighted scoring (no API calls needed)
- Dependency-aware execution loop with timing and metrics
- Persistent route state (save/load JSON)
- Configuration via `.routesmit.toml` and environment variables
- MCP-compatible JSON-RPC 2.0 stdio server
- Structured observability with JSON logging and `timed()` context manager
- Route metrics with token economics and effectiveness scoring
- CLI commands: `run`, `explain`, `detect-host`, `capabilities`, `serve`, `install`
- Install adapters for generating host-specific configs
- 155 tests, all passing without live API calls
