# Personal Engineering Automation — Master Prompt and Folder Structure
## One reusable setup, built once, grown as real needs surface

This is not a training lab. This is the actual folder you work out of
every day. Built once with the prompt below, then extended one real
need at a time using the same discipline.

---

## The folder structure

```
my-work/
├── CLAUDE.md                        # role, product facts, rules — always loaded
├── AGENTS.md                        # only if you also use Codex/other agents
│
├── .claude/
│   ├── commands/                    # slash commands — things you type most days
│   │   ├── status-update.md
│   │   ├── escalation-summary.md
│   │   ├── known-pattern-check.md
│   │   └── eod-queue-report.md
│   │
│   ├── skills/                      # repeatable workflows with judgement in them
│   │   └── checkout-failure-investigation/
│   │       ├── SKILL.md             # trigger, steps, decision points
│   │       └── reference.md         # optional — detail loaded only if needed
│   │
│   └── mcp.json                     # MCP server connections — config, not code
│
├── runbooks/                        # referenced BY CLAUDE.md, not inlined into it
│   ├── stock-oversell.md
│   ├── coupon-double-redemption.md
│   └── fraud-hold-escalation.md
│
└── logs/
    └── eod-reports/                 # output of scheduled/manual report runs
        └── 2026-08-19.md
```

**Why this shape, not a flatter one:**

`CLAUDE.md` stays short because everything long lives in `runbooks/`
and gets referenced, not inlined — this is the "point, don't paste"
rule applied to your own tooling. `commands/` and `skills/` are
separate because they are different mechanisms with different
lifecycles: a command is a fixed template, a Skill has a
`SKILL.md` describing a decision process. `mcp.json` is config only —
if you ever need a real MCP server *built*, that is a separate
software project, not a file in this folder.

There is deliberately no `orchestrator/` folder. If Step 4 below ever
produces a genuine yes, that becomes its own repository — scheduled
jobs and unattended agents are infrastructure, not a subfolder of your
personal working directory.

---

## The master prompt

Run this once to seed the folder. Re-run Step 1 alone whenever a new
need shows up during the week — don't wait for a big rebuild.

```
Role: help me build my own reusable engineering automation setup for
day-to-day work. This is production tooling I will use daily, not a
one-off task and not a training exercise.

MY ROLE
<title, what you're responsible for, who you report to, what "done"
looks like for a typical day>

DOMAIN / PRODUCT
<the actual system(s) you work on, named precisely>

OUTPUT TARGET
Write real files into this structure:
  CLAUDE.md
  .claude/commands/*.md
  .claude/skills/<skill-name>/SKILL.md
  .claude/mcp.json  (config only, do not write server code)
  runbooks/*.md

===================================================================
STEP 1 — CLASSIFY BEFORE BUILDING
===================================================================
List every need I might be tempted to over-build. For each, classify
against exactly these six, in this order, and stop at the first
honest fit — do not skip ahead to a more advanced mechanism:

  1. CLAUDE.md fact       — standing, rarely-changing truth
  2. Slash command        — same shape every time, typed most days
  3. Skill                — repeatable, but needs judgement at each step
  4. MCP server            — needs a real system outside this repo
  5. Sub-agent (Task)      — one-off bounded investigation, thrown away
  6. Orchestrator/headless — must run with NO human present

Show the classification as a table: need | mechanism | one-line why.
Do not build anything in this step.

===================================================================
STEP 2 — WRITE CLAUDE.md
===================================================================
Sections only: role and responsibilities, product facts I need
repeated back accurately (system names, terminology, escalation
ownership), non-negotiable behaviour rules, report format for any
investigation you do on my behalf.

Rules for this file specifically:
  - No explanation, no theory — only things that change your behaviour
  - Anything longer than 3 lines on one topic goes in runbooks/ instead,
    referenced by filename, not inlined
  - Under 60 lines total. If it's longer, something belongs in a
    runbook instead.

===================================================================
STEP 3 — WRITE SLASH COMMANDS
===================================================================
Only for needs classified as "slash command" in step 1. For each:
  - Filename and trigger phrase
  - What it asks me for (the parameters that vary)
  - What it produces, in what format
  - One worked example with realistic values

Write each as its own file under .claude/commands/.

===================================================================
STEP 4 — WRITE THE SKILL(S)
===================================================================
Only for needs classified as "Skill" in step 1. For each:
  - Trigger description — when this should fire, and only then
  - Numbered steps, with the judgement call named explicitly at each
    step that has one
  - What should make it stop and ask me, rather than guess
  - What "done" looks like

If a Skill's evidence would be better sourced live instead of pasted
in by me, note that and link it to the matching MCP entry in step 5 —
don't duplicate reasoning between them.

Write as .claude/skills/<name>/SKILL.md.

===================================================================
STEP 5 — SPECIFY MCP NEEDS (DO NOT BUILD SERVERS)
===================================================================
Only for needs classified as "MCP server" in step 1. For each:
  - System name
  - Tools it would need to expose, read-only vs write, explicitly
  - Which Skill or command from steps 3-4 would consume it
  - Confirmation this is read-only unless a write is genuinely
    required — if write, flag that it needs a separate approval-gate
    design, not silent inclusion

Write this as a spec inside .claude/mcp.json comments or a paired
mcp-requirements.md — do not write server implementation code.

===================================================================
STEP 6 — WRITE RUNBOOKS
===================================================================
For anything referenced from CLAUDE.md by filename rather than
inlined: write the actual runbook. Known failure patterns, standard
resolutions, escalation detail. These can be as long as they need to
be — length is fine here because they load only when referenced, not
on every request.

===================================================================
STEP 7 — HONEST ORCHESTRATOR CHECK
===================================================================
Review everything classified so far. Answer plainly: is there
anything here that genuinely needs to run with no human present, on
a schedule, connected to external systems?

If no — say so, and stop. Do not propose one to seem thorough.

If yes — for each candidate:
  - Exact trigger
  - Step by step what it does
  - Where a human approval gate is still required before any write
    to a live system
  - What happens if it fails partway through
  - Note explicitly that this becomes its OWN repository, not a
    folder inside my personal working directory

===================================================================
STEP 8 — REPORT
===================================================================
List every file written, and for each: which of the six mechanisms
it is, and the one-line justification from step 1 that earned it a
place. If anything from step 1 didn't make it into a file, say why —
usually because it was correctly rejected at every rung.
```

---

## The re-run prompt — for one new need mid-week

Don't rebuild everything each time something new comes up. Run this
instead, and only add the file the answer actually earns.

```
New need, mid-week: <describe it>

Existing setup: <paste current CLAUDE.md, or point at the folder>

Classify this single need against the six mechanisms, in order,
stopping at the first honest fit. Show your reasoning for why it
is NOT each mechanism above the one you land on — I want the
rejections, not just the answer.

If it lands on CLAUDE.md or a slash command, write the addition now.
If it lands on a Skill or MCP requirement, draft it but do not treat
this as automatically approved — ask me to confirm before we add it
to the folder, since those cost more to maintain than a one-line
CLAUDE.md fact.
```

**Why the re-run prompt is stricter than the master prompt for Skills
and MCP entries:** the master prompt runs once, deliberately, with
full attention. Mid-week additions happen under time pressure, which
is exactly when over-building is likeliest — asking Claude to justify
the rejections, not just state the answer, and requiring your
confirmation before anything heavier than a slash command gets added,
keeps the folder from accumulating unused Skills nobody actually uses
twice.

---

## What good output looks like, structurally

A folder that stays mostly `CLAUDE.md` and `.claude/commands/`, with
one or two real Skills that get used weekly, and — for most roles —
an empty `mcp.json` and no orchestrator repository at all. If your
folder tips the other way, heavy on Skills and orchestrator
candidates, re-run step 7 more skeptically before building the next
one.

---
