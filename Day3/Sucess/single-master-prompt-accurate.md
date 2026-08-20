# Single Master Prompt — Build the Entire Setup, Accurately
## One prompt. Run it once. It forces the right questions before building anything.

Paste this into Claude Code, in an empty working directory. The first
thing it does is refuse to guess your role — that was the actual flaw
in every prior attempt in this thread, and this version closes it.

---

```
Role: help me build my own reusable engineering automation setup for
day-to-day work, written as real files in this folder. This is
production tooling I will use daily — not a lab, not a demo.

===================================================================
STEP 0 — DO NOT GUESS. ASK FIRST.
===================================================================
Before doing anything else, ask me these questions and wait for my
answers. Do not proceed on assumed or inferred answers, even
plausible ones:

  1. My exact title and what it actually means day to day where I
     work — not the generic definition of the title, MY version of it.
  2. Who I report to, and what "a good day" looks like concretely —
     what state do things need to be in by end of day.
  3. The real name(s) of the system(s) or product(s) I work on.
  4. Is my work mostly REACTIVE (something breaks or arrives, I
     respond) or mostly EVALUATIVE (I review, decide, set direction
     before anything happens)? Most roles are a mix — tell me the
     rough split.
  5. List 5-8 things you actually did in the last two weeks that felt
     repetitive or that you had to explain to a colleague more than
     once.

Once I answer, restate my role back to me in two sentences and
confirm it's accurate before continuing. If anything I said is
ambiguous, ask a follow-up rather than resolving the ambiguity
yourself.

===================================================================
STEP 1 — CLASSIFY EACH REAL NEED, IN ORDER, STOP AT FIRST FIT
===================================================================
Using my answer to question 5 as the actual list of needs — not
invented ones — classify each against exactly these six, in this
order. Stop at the first honest fit for each; do not skip ahead:

  1. CLAUDE.md fact       — standing, rarely-changing truth
  2. Slash command        — same shape every time, typed most days
  3. Skill                — repeatable, but needs real judgement per step
  4. MCP server            — needs a real system outside this repo
  5. Sub-agent (Task)      — one-off bounded investigation, thrown away
  6. Orchestrator/headless — must run with NO human present, verify
     this against the REACTIVE/EVALUATIVE answer from step 0 — a
     mostly-reactive role rarely justifies this, a mostly-evaluative
     one with a high-frequency trigger sometimes does

Present as a table: need | mechanism | one-line why, referencing my
actual answers, not generic examples.

===================================================================
STEP 2 — WRITE CLAUDE.md
===================================================================
Sections: role and responsibilities (from step 0, in my actual words
where possible), product facts I need repeated back accurately,
non-negotiable behaviour rules specific to what could go wrong in MY
role if you got something wrong, report format for anything you
investigate for me.

No theory, no explanation. Under 60 lines. Anything longer goes into
a runbook referenced by filename, not inlined.

===================================================================
STEP 3 — WRITE SLASH COMMANDS
===================================================================
Only for step-1 items classified as slash commands. Each as its own
file: trigger, what it asks for, what it produces, one worked example
using realistic values from my actual domain.

===================================================================
STEP 4 — WRITE SKILLS
===================================================================
Only for step-1 items classified as Skills. Each: trigger, numbered
steps with the judgement call named explicitly at each step that has
one, what should make it stop and ask me rather than guess, what
"done" looks like. If a Skill would benefit from live data rather
than me pasting it in, note that and link it to step 5.

===================================================================
STEP 5 — SPECIFY MCP NEEDS, DO NOT BUILD SERVERS
===================================================================
Only for step-1 items classified as needing an MCP server. Name the
system, list tools as read-only or write EXPLICITLY, name which Skill
or command consumes each, and flag that any write-capable tool needs
a separate approval-gate design before it gets built — do not include
write access by default.

===================================================================
STEP 6 — WRITE RUNBOOKS
===================================================================
Anything referenced from CLAUDE.md by filename gets written here in
full. Length is fine — these load only when referenced.

===================================================================
STEP 7 — HONEST ORCHESTRATOR CHECK
===================================================================
Re-examine every step-1 item classified as needing rung 6. For each,
answer plainly: does this need to run with no human present, and is
the trigger frequency genuinely beyond what a human could reasonably
run manually?

If every candidate resolves to "no" or "a scheduled read-only report
is enough" — say so and stop. Do not propose an orchestrator to seem
thorough.

If a genuine candidate survives — state its exact trigger, what it
does step by step, where a human approval gate remains required
before any write to a live system, what happens on partial failure,
and note explicitly that this becomes its own separate repository,
not a folder inside this one.

===================================================================
STEP 8 — WRITE THE FILES AND REPORT
===================================================================
Create the actual folder structure:

  CLAUDE.md
  .claude/commands/*.md
  .claude/skills/<name>/SKILL.md
  .claude/mcp.json  (config/spec only, never server implementation code)
  runbooks/*.md

Then report: every file written, which of the six mechanisms it is,
and the one-line justification from step 1 that earned it a place.
For anything from my step-0 list that produced NO file, say
explicitly why it was rejected at every rung — that is not a gap,
that is the process working.

===================================================================
STEP 9 — MID-WEEK ADDITION RULE, FOR LATER USE
===================================================================
Tell me, for future reference, the exact prompt shape I should use
when a new need comes up mid-week: it must go through the same
six-rung classification, show the rejected mechanisms above the one
it lands on, and require my explicit confirmation before anything
heavier than a slash command gets added to this folder.
```

---

## What makes this version different from every prior attempt

**Step 0 refuses to proceed on assumption.** Every worked example
built earlier in this session guessed at role details and flagged the
guess after the fact. This version makes the guess structurally
impossible — there is no step 1 without real answers to step 0.

**Step 1 classifies your actual list, not invented examples.**
Question 5 in step 0 produces real repetitive tasks from your last two
weeks. Step 1 runs the classification against those, not against
plausible-sounding retail or architecture scenarios.

**Step 7's orchestrator check is tied back to step 0's
reactive/evaluative answer**, not judged in isolation. A reactive role
claiming it needs an orchestrator gets more scrutiny than an
evaluative one with a genuinely high-frequency trigger — because the
two prior worked examples showed that's exactly where the honest
answer differs.

**Step 9 hands you the reusable mid-week prompt as an output of this
run**, so you don't need a second document — this one prompt produces
both the initial folder and the rule for extending it later.

---
