# routesmith - Copilot Instructions

This repository contains `routesmith`, a host-aware auto-routing skill library for IDEs and coding agents.

## Core Architecture Rule

routesmith is a HOST-AWARE skill layer, NOT a universal cross-provider broker.

- In Claude Code: only Claude-family models are managed.
- In Codex/OpenAI: only OpenAI-family models are managed.
- In Copilot: model switching is host-controlled; use prompt optimization.
- Never assume a host can use models from another provider family.

## Key Design Principles

1. **Auto mode is default** — Users should not manually choose models per step.
2. **Capability-first routing** — Map task types to capability classes, then resolve to host models.
3. **Truthful switching** — Never claim a model was switched unless confirmed.
4. **Graceful fallback** — If switching is unsupported, use prompt strategy.
5. **Deterministic planning** — Planner works without API calls.

## Package Structure

- `src/routesmith/` — Main package
- `src/routesmith/hosts/` — Host adapters (detect, capabilities, switch)
- `src/routesmith/install/` — Install adapters for generating host configs
- `src/routesmith/server/` — Stdio server for tool integration
- `tests/` — Test suite (no live API calls required)

## Testing

Tests must run without live API calls. Use mocked behavior for provider-dependent flows.
Host detection, planning, and routing must work without any API keys.
