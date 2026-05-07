# routesmit

**Host-aware auto-routing skill library for IDEs and coding agents.**

routesmit improves task execution in coding agent environments by detecting the current host, inspecting its model capabilities, decomposing mixed prompts into subtasks, and routing each step to the best available host-compatible model.

## Why Host-Aware Routing?

Most coding agents run inside a specific host environment (Claude Code, Codex, Copilot, Cursor, Aider). Each host has different:
- Available model families
- Model switching capabilities
- Configuration surfaces
- Instruction file support

**routesmit does NOT assume all IDEs can freely mix providers.** It inspects what the current host supports, then routes within those constraints.

| Host | Model Family | Dynamic Switch | Strategy |
|------|-------------|----------------|----------|
| Claude Code | Anthropic only | ✓ | Model switching per task |
| Codex | OpenAI only | ✓ | Model switching per task |
| Copilot | Mixed (host-controlled) | ✗ | Prompt optimization |
| Cursor | Mixed (user-controlled) | ✗ | Prompt optimization |
| Aider | Mixed | ✓ | Model switching per task |
| Generic | Unknown | ✗ | Prompt optimization |

## Auto Mode (Default)

Auto mode is the default and recommended mode. For a single mixed prompt, routesmit automatically:

1. Detects the host environment
2. Inspects host model capabilities
3. Classifies the prompt into task types
4. Splits it into ordered subtasks
5. Chooses the best host-compatible model per subtask (when possible)
6. Executes or recommends the route
7. Returns a route summary and advisory messages

## Architecture

```
┌─────────────────────────────────────────┐
│              CLI / Integration           │
├─────────────────────────────────────────┤
│         Core Orchestration Layer         │
│  Planner → Policy → Router → Executor   │
├─────────────────────────────────────────┤
│           Host Adapter Layer             │
│  detect → capabilities → switch/prompt  │
└─────────────────────────────────────────┘
```

### Capability Classes

Instead of hardcoding model names, routesmit uses abstract capability classes:

- **deep_reasoning** — Planning, analysis, review
- **coding** — Implementation, testing, refactoring
- **balanced** — Documentation, general tasks
- **fast** — Formatting, simple transformations

Each host adapter maps these to actual host-supported models.

### Task Types

- `planning` — Design and architecture
- `analysis` — Research and investigation
- `coding` — Implementation
- `testing` — Test creation and validation
- `refactor` — Code improvement
- `documentation` — Docs and comments
- `formatting` — Style and linting
- `review` — Quality review

## Installation

```bash
pip install routesmit
```

## CLI Usage

```bash
# Run a prompt through the routing pipeline
routesmit run "Plan this feature, implement it, add tests, and write docs"

# Explain the route plan without executing
routesmit explain "Refactor the auth module and add integration tests"

# Detect the current host
routesmit detect-host

# Show host capabilities
routesmit capabilities

# Run diagnostics
routesmit doctor

# Install config for a target host
routesmit install claude
routesmit install codex
routesmit install copilot
routesmit install cursor
routesmit install aider

# Start stdio server for tool integration
routesmit serve-stdio
```

## Python API

```python
import routesmit

# Run a prompt (auto mode)
result = routesmit.run("Plan and implement a REST API with tests")

# Explain without executing
plan = routesmit.explain_route("Refactor the database layer")

# Detect host
host = routesmit.detect_host()

# Get capabilities
caps = routesmit.get_host_capabilities()
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROUTESMIT_DEFAULT_MODE` | Default execution mode | `auto` |
| `ROUTESMIT_ALLOW_MODEL_SWITCH` | Allow model switching | `true` |
| `ROUTESMIT_FORCE_HOST` | Force a specific host | — |
| `ROUTESMIT_DEFAULT_HOST` | Default host fallback | — |
| `ROUTESMIT_DEBUG` | Enable debug output | `false` |
| `ROUTESMIT_ENABLE_TELEMETRY` | Enable telemetry | `false` |

## Model Switching Limits

**routesmit is truthful about model switching:**

- If a host supports dynamic switching, routesmit will attempt it.
- If a host does NOT support switching, routesmit will NOT fake it.
- The run result always indicates whether switching was applied or prompt strategy was used instead.
- Advisory messages inform the user of any limitations.

## Prompt Strategy Fallback

When a host cannot switch models dynamically, routesmit still provides value:

1. **Task decomposition** — Breaking complex prompts into focused steps
2. **Dependency ordering** — Ensuring steps execute in correct order
3. **Prompt optimization** — Structuring each step's prompt for best results
4. **Capability advisory** — Recommending ideal model classes per step

## Pinned Model Behavior

If a user manually pins a model:
- That choice is honored for all tasks.
- An advisory message is shown recommending Auto mode for mixed tasks.

## Supported Hosts

### Claude Code
- Manages Claude-family models (Opus, Sonnet, Haiku)
- Supports dynamic model switching
- Uses CLAUDE.md for repo instructions

### Codex (OpenAI)
- Manages OpenAI-family models (o3, codex-mini, GPT-4.1)
- Supports dynamic model switching via flags
- Uses AGENTS.md for repo instructions

### GitHub Copilot
- Model selection is host-controlled
- Uses `.github/copilot-instructions.md` and prompt files
- Applies prompt optimization strategy

### Cursor
- Model selection is user-controlled
- Uses `.cursorules` for guidance
- Applies prompt optimization strategy

### Aider
- Supports multiple providers
- Model switching via `--model` flag
- Uses `.aider.conf.yml` for configuration

## Roadmap

- [ ] MCP tool integration
- [ ] Real-time model performance tracking
- [ ] Cost-aware routing
- [ ] Custom policy configuration
- [ ] Plugin system for additional hosts

## License

MIT
