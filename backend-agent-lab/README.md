# backend-agent-lab

A multi-agent performance-engineering workflow for backend developers:
structured product knowledge feeding one orchestrator, nine specialist
agents, deterministic testing tools, an evidence store, and human
approval gates. Built to operate against
[`taskflow-ops`](../taskflow-ops), the backend service in this same
workspace.

## Why this shape

Nine narrow agents instead of one broad one, for the same reason RxFlow's
parallel-review lab used five isolated worktrees instead of one reviewer
covering everything: bounded scope makes each agent's output checkable,
and a reviewer (agent 9) who didn't write the change is the only one
positioned to catch what its author can't see in their own work.

## Structure

```
knowledge/       structured product knowledge — see knowledge/README.md
                 for what's real vs. what's an acknowledged gap
agents/          9 agent instruction templates, one shared format
evidence/        append-only record of what each agent run actually
                 found — never overwritten, one file per run
tools/           the deterministic testing tools (real k6/curl scripts,
                 not agent-generated ad hoc commands)
```

## Build stages

- **Stage 1 — Manual.** Each `agents/*/AGENT.md` is a standalone prompt.
  Run one at a time by hand, paste the previous agent's output into the
  next. Proves the instructions are right before automating anything.
- **Stage 2 — Semi-automated.** `agents/orchestrator/orchestrate.py`
  sequences all 9 agents, writes real evidence files, and hard-pauses
  for typed human confirmation at the tuning and independent-review
  gates. **This is what's built and run in this repo.**
- **Stage 3 — Controlled automation.** The deterministic stages
  (discovery → execution → analysis) run unattended; the tuning and
  review gates still require a human, always — see
  `agents/independent-review/AGENT.md` for why that one is
  non-negotiable even at full automation.

## The one rule every agent follows

An agent that cannot produce real evidence for a claim states the gap
explicitly (`knowledge/objectives/` and `knowledge/traffic/` are
intentionally empty in this repo right now — see
`knowledge/README.md`) rather than inventing a plausible-sounding
default. An agent that fabricates a missing SLO or a missing traffic
shape to keep the pipeline moving is the exact failure mode this
architecture exists to prevent.
