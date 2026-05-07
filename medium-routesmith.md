# Stop Treating Mixed Prompts Like One Task

*A host-aware routing layer that turns mixed coding prompts into structured workflows — without replacing the agent you already use.*

I kept running into the same stupid moment.

I would open a coding agent, type one big prompt, and get exactly what these tools promise at their best: momentum.

"Plan this feature, implement it, add tests, write docs, and review the final result."

For a few minutes, it felt great. One prompt. One flow. One clean path from idea to shipped change.

Then the flow broke.

I stopped thinking about the feature and started doing manual routing in my head.

Should planning use a stronger reasoning model?

Should coding use something faster or cheaper?

Should tests use the same model as implementation?

Does this host even support real switching, or am I just assuming it does?

Why am I spending the heaviest model in the stack on README edits and formatting?

That was the point where the problem became obvious.

I was not blocked by the model. I was blocked by the workflow.

That prompt was not one task. It was planning, coding, testing, docs, and maybe review compressed into one sentence.

That is the gap that led me to build RouteSmith.

![One coding prompt branching into multiple task-specific workstreams inside an IDE and terminal workflow.](./assets/routesmith-hero.svg)

## Mixed Prompts Are Workflows

Most coding-agent workflows still treat a prompt like a single request.

Real development work is rarely shaped that way.

When someone says, "plan this feature, implement it, add tests, write docs," they are not asking for one thing. They are asking for several different kinds of work:

- planning
- analysis
- implementation
- testing
- documentation
- often review and cleanup at the end

Those steps do not need the same kind of model. They do not need the same reasoning depth, the same latency profile, or the same cost profile.

And they definitely do not behave the same across Claude Code, Cursor, Copilot, Codex, Gemini CLI, or Aider.

That last part matters.

There is a lot of talk about multi-model workflows, but in practice the host decides what is actually possible. Some hosts support real dynamic switching. Some mostly control the model surface themselves. Some let you influence routing indirectly. Some make it very easy to believe you have more control than you really do.

I wanted a layer that works with that reality instead of smoothing it over with fake abstraction.

## What RouteSmith Actually Is

RouteSmith is a host-aware routing layer for coding agents.

It is not another coding agent.

It is not an API gateway.

It sits between a mixed prompt and the host's real capabilities.

The job is straightforward:

1. Detect the host.
2. Break the prompt into task types.
3. Map those tasks to capability classes.
4. Resolve those capabilities against what the current host can actually do.
5. Switch models when the host supports it.
6. Fall back honestly when the host does not.
7. Track outcomes over time so routing gets better.

That means RouteSmith is not trying to replace Claude Code, Cursor, Aider, Copilot, or anything else you already use. It is trying to make mixed-task workflows behave more intelligently inside those environments.

## Who This Is For

One mistake I think people make when they talk about routing is assuming only power users care.

I think that misses a big part of the story.

RouteSmith is also for people who are just getting started with coding agents and do not want to think about model choice all day.

That includes a lot of people getting into vibe coding right now.

If you are early in that workflow, the friction usually is not writing the prompt. The friction starts right after the prompt.

You begin second-guessing things like:

- Should I use the smartest model for everything?
- Should I switch between planning and coding?
- Is this task too simple for an expensive model?
- Is the host actually switching, or am I just assuming it is?

Most people should not have to become part-time routing engineers before they can build something useful.

That is a big part of why RouteSmith exists.

It is for two groups at the same time:

- people who want better control over routing
- people who want less manual model decision-making

That second group is probably bigger.

More concretely, RouteSmith is a good fit for:

### 1. People new to coding agents

If you are using Claude Code, Cursor, Copilot, Codex, Gemini CLI, or Aider and you do not yet have strong intuition for model tradeoffs, RouteSmith is meant to reduce that burden.

You should be able to describe the work in plain language and let the routing layer do the decomposition.

### 2. People doing vibe coding

If your style is, "build this feature, wire the API, add tests, clean up the docs," RouteSmith helps because it treats that prompt like a workflow instead of a blob.

### 3. Solo builders and founders

Solo builders usually mix planning, implementation, testing, docs, and review in one session because they are doing all of it themselves.

That is exactly where task-aware routing starts paying off.

### 4. Teams that want consistency

Without a routing layer, every developer ends up inventing their own model habits.

RouteSmith gives you a more explainable and repeatable path.

### 5. Advanced users who care about control

If you care about host constraints, routing logic, policy overrides, plugins, observability, and performance-aware switching, RouteSmith has room for that too.

## How the Routing Works

The flow is intentionally simple.

![Flow diagram showing host detection, task classification, capability mapping, routing, execution, and telemetry feedback.](./assets/routesmith-flow.svg)

### Step 1: Detect the host

RouteSmith starts by detecting where it is running.

The host is not a footnote. It decides what model families are relevant, what switching is possible, and how honest the router can be about execution.

### Step 2: Classify the prompt into task types

RouteSmith uses deterministic planning to classify prompts into task types like planning, analysis, coding, testing, refactor, documentation, formatting, and review.

I care about this being deterministic because planning should not require live API calls just to understand the shape of the work.

### Step 3: Map task types to capability classes

Instead of hardcoding everything directly to model names, RouteSmith maps tasks to capability classes such as:

- `deep_reasoning`
- `coding`
- `balanced`
- `fast`

That gives the system a portable abstraction layer. A planning task can ask for deep reasoning without assuming every host exposes the same model names or the same controls.

### Step 4: Resolve capabilities against the current host

This is where RouteSmith becomes host-aware instead of generic.

If the host supports dynamic switching, RouteSmith can suggest concrete models per task.

If the host does not support switching, RouteSmith does not fake it. It keeps the routing intelligence, applies prompt strategy, and tells you what actually happened.

That truthful behavior is one of the core design decisions in the project.

### Step 5: Preserve dependency order

Mixed prompts are not just lists. They are dependency graphs.

Tests often depend on implementation. Docs usually make more sense after the change exists. Review is usually last.

RouteSmith keeps that order intact so the route matches the actual structure of the work.

### Step 6: Learn from real outcomes

RouteSmith also records local performance data, including model used, host name, task type, capability class, success or failure, duration, and telemetry source.

That is useful for visibility on its own, but it also does something more valuable: it can become an active routing signal.

If a default model has enough evidence showing weak success or poor latency for a capability, and a better host-available option exists, RouteSmith can de-prioritize the weaker default.

That turns performance tracking from passive reporting into routing feedback you can actually use.

## A Few Concrete Examples

### The beginner building an expense tracker

Imagine someone fairly new to coding agents asks for this:

"Build me a simple expense tracker with authentication, add tests, and write a README."

That user may not know which model is better for planning versus coding versus docs. They probably do not want to know. They just want the thing built.

RouteSmith helps by decomposing that request into task-level work and routing each phase with the host's real constraints in mind.

### The founder shipping a feature fast

A solo founder might say:

"Plan the feature, implement the API, add tests, update docs, and review the final diff."

That is a classic mixed-task workflow. Without routing, it becomes one long interaction on one model. With RouteSmith, it becomes a structured sequence.

### The user on a constrained host

Some hosts expose model control directly. Some do not.

That difference creates friction when tooling assumes universal switching. RouteSmith helps by being explicit: if switching is available, it uses it. If it is not, it falls back honestly.

## Where RouteSmith Fits

I do not think the honest pitch here is that nothing similar exists.

![Diagram showing agent products, RouteSmith as a routing layer, and API gateway infrastructure as separate layers.](./assets/routesmith-positioning.svg)

There are good products around this space. They mostly solve different layers of the stack.

Claude Code, Cursor, and Aider are agent products. They are the tools doing the work.

LiteLLM and Portkey are model and gateway infrastructure. They normalize providers, manage routing at the API layer, and add control, visibility, and governance around model traffic.

Rules, skills, and instruction files are customization layers. They shape behavior, but they are not really routing brains by themselves.

RouteSmith sits in the gap between those layers.

It is not trying to become a full IDE. It is not trying to become a universal API gateway. It is not just another instructions file.

It is a routing layer for coding-agent workflows.

If I had to summarize it simply:

- if you want a coding agent, use Claude Code, Cursor, or Aider
- if you want API-layer multi-provider routing, use LiteLLM or Portkey
- if you want a host-aware routing layer for mixed coding prompts, that is where RouteSmith fits

That is the lane.

## Why I Built It This Way

I do not think the useful future for coding agents is one model doing everything.

I also do not think the useful future is pretending every host is the same.

The more practical direction is:

- let the user describe the work naturally
- let the system understand the shape of the work
- let routing happen at the task level
- let the host remain the source of truth about what is actually possible
- let the feedback loop improve over time

That is the design RouteSmith is pushing toward.

## Try It

If you want to get a feel for it, the simplest path is:

```bash
pip install routesmith
routesmith detect-host
routesmith explain "Refactor auth, add tests, write docs"
routesmith run "Refactor auth, add tests, write docs"
routesmith stats
```

And if you are building tooling around agents, you can expose the routing layer over stdio with:

```bash
routesmith serve-stdio
```

## Final Thought

The most interesting part of coding-agent workflows is no longer just the model.

It is the routing layer around the work.

If a prompt contains planning, implementation, testing, documentation, and review, then treating it like one undifferentiated request leaves a lot on the table.

RouteSmith is my attempt to make that layer explicit, host-aware, and useful for both advanced users and people who are just getting started.

You should not need to know a full model matrix before you can build something real.

That is the job I want RouteSmith to take off your plate.

---

Project: [github.com/sidrat2612/routesmith](https://github.com/sidrat2612/routesmith)  
PyPI: [pypi.org/project/routesmith](https://pypi.org/project/routesmith/)