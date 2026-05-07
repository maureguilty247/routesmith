<p align="center">
  <h1 align="center">routesmith</h1>
  <p align="center">
    <strong>Host-aware auto-routing for coding agents</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/routesmith/"><img src="https://img.shields.io/pypi/v/routesmith?color=blue&label=PyPI" alt="PyPI version"></a>
    <a href="https://github.com/sidrat2612/routesmith/actions/workflows/ci.yml"><img src="https://github.com/sidrat2612/routesmith/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://pypi.org/project/routesmith/"><img src="https://img.shields.io/pypi/pyversions/routesmith" alt="Python versions"></a>
    <a href="https://github.com/sidrat2612/routesmith/blob/main/LICENSE"><img src="https://img.shields.io/github/license/sidrat2612/routesmith" alt="License"></a>
    <a href="https://github.com/sidrat2612/routesmith/stargazers"><img src="https://img.shields.io/github/stars/sidrat2612/routesmith?style=social" alt="Stars"></a>
  </p>
</p>

---

**routesmith** automatically routes coding agent tasks to the best available model in your IDE — no manual model picking, no cross-provider hacks.

> Give it a mixed prompt like *"Plan this feature, implement it, add tests, write docs"* and it decomposes, routes each step to the right capability class, and executes using your host's native model switching.

## Why?

Most coding agents are stuck on one model. Mixed tasks (plan → code → test → document) benefit from different model strengths. But each IDE host (Claude Code, Codex, Copilot, Cursor, Aider) has different model families and switching capabilities.

**routesmith solves this** by being host-aware:

| Host | Models | Strategy |
|------|--------|----------|
| Claude Code | Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5 | Dynamic model switching |
| Codex | GPT-5.5 / GPT-5.4 / GPT-5.3-Codex | Dynamic model switching |
| Copilot | Claude 4.7 / GPT-5.5 / Gemini 3.1 Pro (plan-dependent) | Prompt optimization |
| Cursor | Claude 4.7 / GPT-5.5 / GPT-5.3-Codex / Gemini 3.1 Pro | Prompt optimization |
| Aider | Claude 4.7 / GPT-5.5 / Gemini 3.1 Pro | Dynamic model switching |

## Quickstart

```bash
pip install routesmith
```

```python
import routesmith

# Auto-detect host, decompose, route, execute
result = routesmith.run("Plan and implement a REST API with tests")

# Just see the plan without executing
plan = routesmith.explain_route("Refactor the database layer")

# Check what you're running on
host = routesmith.detect_host()
caps = routesmith.get_host_capabilities()
```

### CLI

```bash
# Route a prompt
routesmith run "Plan this feature, implement it, add tests, and write docs"

# Preview the route plan
routesmith explain "Refactor auth module and add integration tests"

# Diagnostics
routesmith detect-host
routesmith capabilities
routesmith doctor
```

## How It Works

routesmith is an **advisory routing layer** — it plans and recommends, it does not replace your host's execution engine.

```
┌─────────────────────────────────────────┐
│           Your Prompt                   │
├─────────────────────────────────────────┤
│  1. Detect host (Claude Code? Copilot?) │
│  2. Decompose into typed subtasks       │
│  3. Map tasks → capability classes      │
│  4. Resolve to host-native models       │
│  5. Switch models or optimize prompts   │
│  6. Report metrics & effectiveness      │
└─────────────────────────────────────────┘
```

### What it does

- **Decomposes** mixed prompts into discrete, typed subtasks
- **Routes** each subtask to the best capability class (`deep_reasoning`, `coding`, `balanced`, `fast`)
- **Switches models** when the host supports it (Claude Code, Codex, Aider)
- **Falls back to prompt optimization** when the host controls model selection
- **Reports** timing, token estimates, effectiveness scores

### What it does NOT do

- Does **not** make LLM API calls — the host handles execution
- Does **not** bypass host constraints — works within your IDE's limits
- Does **not** fake model switches — tells you honestly what happened

### Design Philosophy

Coding agents run inside a host that owns the LLM connection. routesmith sits *alongside* the host as a skill layer that makes smarter routing decisions. It's the routing brain, not the execution muscle.

## Capability Classes

Instead of hardcoding model names, routesmith uses abstract capability classes:

| Class | Use Case | Example Models |
|-------|----------|----------------|
| `deep_reasoning` | Planning, architecture, review | Claude Opus 4.7, GPT-5.5 |
| `coding` | Implementation, testing, refactoring | Claude Sonnet 4.6, GPT-5.3-Codex |
| `balanced` | Documentation, general tasks | Claude Sonnet 4.6, GPT-5.4 |
| `fast` | Formatting, simple transforms | Claude Haiku 4.5, GPT-5.4-mini |

Each host adapter maps these to actual available models.

## Task Types

routesmith classifies prompts into: `planning`, `analysis`, `coding`, `testing`, `refactor`, `documentation`, `formatting`, `review`

Dependencies are resolved automatically — tests wait for code, docs wait for implementation.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROUTESMITH_DEFAULT_MODE` | Execution mode | `auto` |
| `ROUTESMITH_ALLOW_MODEL_SWITCH` | Allow model switching | `true` |
| `ROUTESMITH_FORCE_HOST` | Force a specific host | — |
| `ROUTESMITH_DEBUG` | Enable debug output | `false` |

### Config File

Create `.routesmith.toml` in your project root:

```toml
[routesmith]
default_mode = "auto"
allow_model_switch = true
```

## MCP / Stdio Server

routesmith exposes an MCP-compatible JSON-RPC 2.0 server for tool integration:

```bash
routesmith serve-stdio
```

This lets IDE extensions and agents call routesmith as a tool.

## Install Configs for Hosts

Generate host-specific configuration files:

```bash
routesmith install claude    # Writes CLAUDE.md
routesmith install codex     # Writes AGENTS.md
routesmith install copilot   # Writes .github/copilot-instructions.md
routesmith install cursor    # Writes .cursorrules
routesmith install aider     # Writes .aider.conf.yml
```

## Auto Mode (Default)

Auto mode is the default. For a single mixed prompt, routesmith:

1. Detects the host environment
2. Classifies the prompt into task types
3. Splits into ordered subtasks with dependency resolution
4. Chooses the best host-compatible model per subtask
5. Executes (or recommends) the route
6. Returns metrics and advisory messages

### Truthful Switching

- If the host supports dynamic switching → routesmith switches
- If the host does NOT support switching → routesmith uses prompt strategy
- The result always tells you exactly what happened — no black boxes

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/sidrat2612/routesmith.git
cd routesmith
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Roadmap

- [x] Host detection and capability mapping
- [x] Weighted task decomposition planner
- [x] Dependency-aware execution loop
- [x] Persistent route state
- [x] MCP stdio server
- [x] Structured observability
- [ ] Real-time model performance tracking
- [ ] Cost-aware routing
- [ ] Custom policy plugins
- [ ] Additional host adapters

## License

[MIT](LICENSE) — use it anywhere.

---

<p align="center">
  <sub>Built for the multi-model future of coding agents.</sub>
</p>
