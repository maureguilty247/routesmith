---
mode: agent
description: "Implement or modify routesmith package components"
---

You are working on routesmith, a host-aware auto-routing skill library.

## Key Rules

1. routesmith is host-aware: it works WITHIN the host's model-control surface.
2. Never assume cross-provider model access.
3. Auto mode is the default for all mixed prompts.
4. Capability classes (deep_reasoning, coding, balanced, fast) map to host-specific models.
5. If host cannot switch models, use prompt optimization instead.
6. Planner must work deterministically without API calls.
7. Tests must run without live API calls.

## Architecture Layers

1. **Core**: planner, policy, router, executor, advisory, review
2. **Hosts**: base adapter, detector, per-host adapters
3. **CLI/Integration**: typer CLI, stdio server, install adapters

## When Implementing

- Use Pydantic models for domain types
- Use typer + rich for CLI
- Keep host adapters truthful about capabilities
- Map TaskType -> CapabilityClass -> host model (not direct TaskType -> model)
- Never hardcode provider-specific model names in core logic
