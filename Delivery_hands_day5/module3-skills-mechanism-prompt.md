# Module 7 — Choosing the Right Mechanism, Applied to RxFlow
## Six Skills, correctly built — and correctly rejected where they shouldn't exist

Your table now has eight rows, not six — **hooks** and **headless/CI**
are both distinct from what earlier exercises in this thread tested.
This prompt corrects that gap and connects the six named Skills
directly to RxFlow's real seeded defects.

---

## The eight-row test, restated precisely

| What you need | What you build |
|---|---|
| A one-time constraint | A prompt |
| A standing repository standard | CLAUDE.md |
| Something you type most days | A slash command |
| A repeatable multi-step workflow with judgement | A Skill |
| A rule that must fire whether or not anyone remembers | A hook |
| Access to a system outside the repo | An MCP server |
| A bounded investigation done in isolation | A sub-agent |
| Something that must run with no human present | Headless / CI |

**The row most teams skip past too quickly is the hook row.** A Skill
requires someone to invoke it. A hook requires nothing — it fires on
an event (pre-commit, pre-tool-use, post-edit) regardless of whether
anyone thought to ask. That distinction is the entire reason "rule
that must fire whether or not anyone remembers" gets its own row
instead of folding into Skills.

---

## The prompt

Run inside the built RxFlow repository. If RxFlow doesn't exist yet,
this prompt has nothing real to classify against — build it first.

```
Role: help me build this week's checked-in Skills correctly, and
just as importantly, help me catch anywhere I'm about to build a
Skill that should have been something lighter.

The six Skills for this week: incident diagnosis, migration review,
domain-tuned security review, release readiness, performance
investigation, staged dependency upgrade.

===================================================================
STEP 1 — TEST EACH OF THE SIX AGAINST ALL EIGHT ROWS FIRST
===================================================================
Before building any of the six as a Skill, test each one honestly
against the full eight-row table. Do not assume "Skill" is correct
just because that's what this week's brief calls it.

For each of the six, answer:
  - could this be three lines of CLAUDE.md instead? Why not?
  - could this be a slash command instead? Why not?
  - does any PART of this actually need a hook instead — a rule that
    must fire automatically, not on request? Name it if so.
  - does any part need an MCP server, because it touches a real
    system outside this repo?

Show as a table: skill name | rejected as CLAUDE.md/command because |
confirmed as genuine Skill because | any hook or MCP component found
inside it.

If any of the six is NOT actually a good Skill candidate once tested
honestly, say so plainly rather than building it anyway because it
was on the list.

===================================================================
STEP 2 — BUILD EACH CONFIRMED SKILL WITH FULL ANATOMY
===================================================================
For each Skill confirmed in step 1:

  TRIGGER DESCRIPTION
    Precisely when this should fire, and — as important — when it
    should NOT. A trigger too broad means it fires on things it
    shouldn't; too narrow means it silently doesn't fire when needed.

  PROGRESSIVE CONTEXT LOADING
    What goes in SKILL.md itself (loaded every time it's considered)
    versus what goes in a referenced file (loaded only once the
    Skill actually fires). Getting this split wrong means either the
    Skill is too expensive to even consider, or too thin to be useful
    once running.

  BUNDLED SCRIPTS, ASSETS, TEMPLATES
    What real reusable material does this Skill carry with it —
    from actual RxFlow defects, not generic examples.

  VALIDATION AND FALLBACK
    What does this Skill check before declaring success? What does
    it do if that check fails?

  ERROR REPORTING
    What does honest failure look like — not "something went wrong"
    but the specific thing that couldn't be verified, and why.

===================================================================
STEP 3 — CONNECT EACH SKILL TO A REAL RXFLOW DEFECT
===================================================================
For each Skill, name which of the ten seeded defects it would
actually be exercised against, and how:

  - incident diagnosis → the duplicate lens job, treated as a live
    incident rather than a known lab exercise
  - migration review → the Alembic revision with no downgrade path
  - domain-tuned security review → PII in logs AND the SQL injection,
    both — a security review that only caught one would be incomplete
  - release readiness → run against the branch containing the
    idempotency fix from Lab 3, checking it's actually mergeable
  - performance investigation → the Celery retry amplification —
    turn "it feels like more load" into a real number
  - staged dependency upgrade → not defect-specific; use it on any
    real dependency bump this repo has pending, characterization
    tests first

If a Skill has no real RxFlow defect to exercise against, that is a
signal — either find the genuine connection or reconsider whether it
belongs in this week's checked-in set.

===================================================================
STEP 4 — THE HOOK CHECK, EXPLICITLY
===================================================================
Separately from the six Skills: review the ten seeded defects and
identify which ones represent a rule that should have fired
automatically, regardless of whether an engineer remembered to run a
Skill or ask a question.

For each candidate, specify:
  - the event it should fire on (pre-commit, pre-tool-use, post-edit)
  - what it blocks or flags
  - why a Skill would NOT have been sufficient here — what happens
    if the engineer simply forgets this exists

At minimum, check these three against the hook test explicitly:
  - "never log prescription values or patient identifiers"
  - "every Alembic revision must have a working downgrade()"
  - "services/pricing/ changes require characterization tests FIRST"

For each: is this actually enforced as a hook in this repo, or does
it currently only exist as a CLAUDE.md sentence that depends on
someone reading it? If the latter, say so plainly — a rule written
down but not enforced is not the same as a rule that fires whether
or not anyone remembers, and this repository's CLAUDE.md may be
overstating what it actually guarantees.

===================================================================
STEP 5 — REPORT
===================================================================
List all six Skills with their step 1 justification. List all hook
candidates found in step 4, and state honestly which are real hooks
versus which are currently just written rules pretending to be
enforced. Flag any of the six original Skills that step 1 suggested
should have been something lighter, even if you built it anyway per
the week's brief — the honest classification matters more than
matching the assignment.
```

---

## Why step 4 exists as its own step, not folded into step 1

The six Skills were handed to participants as a list — the temptation
is to build all six and move on. Step 4 forces a second pass that
nobody asked for directly: **go back through the defects and find the
rules that were written down as CLAUDE.md sentences but never actually
enforced as hooks.**

This is where "never log prescription values" earns real scrutiny. If
that rule only exists as a line of text in CLAUDE.md, it is exactly
the failure mode from the earlier diagram's left box — a rule that
only fires if someone remembers to read it. A hook that greps every
diff for the flagged field names before commit is the difference
between a rule that's *stated* and a rule that's *guaranteed*.

---

## The one line worth putting on a slide for this module

**A Skill you have to remember to run is a prompt with better
branding. A hook is the only mechanism on this table that doesn't
need anyone to remember anything.**

---

*Coderrange · corporate training and engineering capability*
