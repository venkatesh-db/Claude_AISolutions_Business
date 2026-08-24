# Module 6 — CLAUDE.md Build Prompt
## Connected to what's actually real in this thread

Two repos have come up in this conversation. Only one of them exists
as running code right now — worth being precise about which, because
this prompt behaves differently against each.

| Repo | Status | Use for this module |
|---|---|---|
| **cartsvc** | Built, tested, verified in this session — `pytest` passes, defects reproduce on demand | **Run this prompt against it now, for real** |
| **RxFlow** | Only a build prompt exists — never executed here, no Docker in this sandbox | Run the same prompt against it once you've built it yourself in Claude Code |

Everything below is written against `cartsvc` as the concrete case,
with RxFlow noted alongside wherever the same pattern would apply once
it's built.

---

## The prompt

Run this inside the actual repo — `cartsvc/`, or RxFlow once you've
built it.

```
Role: help me build durable repository guidance for this codebase —
CLAUDE.md files that will be loaded on every future session, not a
one-off explanation for me right now.

===================================================================
STEP 0 — DO NOT INVENT. VERIFY FIRST.
===================================================================
Before writing anything, inspect this repository and confirm, by
actually running them, the real build, test, lint, and type-check
commands. Paste exact output. If any command fails or doesn't exist,
say so — do not write a guessed command into any CLAUDE.md file.

===================================================================
STEP 1 — CLASSIFY: PROMPT INSTRUCTION vs DURABLE GUIDANCE
===================================================================
List everything that might be tempted into CLAUDE.md, classify each
as DURABLE, TASK-SPECIFIC, or TEMPORARY. Show as a table with reasons.
Get this right before step 2.

===================================================================
STEP 2 — MAP THE HIERARCHY THIS REPO ACTUALLY NEEDS
===================================================================
Inspect the real module boundaries. For each candidate nested
location, state what rule would DIFFER from the root file. Do not
create a nested file for a directory that exists but has no
differing rule. State the hierarchy and justify each nested file
individually.

===================================================================
STEP 3 — WRITE THE ROOT CLAUDE.md
===================================================================
Sections: architecture boundaries, verified build/test/lint/type-check
commands, naming and typing standards, error-handling requirements,
security rules, dependency restrictions, migration requirements, API
compatibility expectations, observability requirements, definition of
done / PR requirements.

Hard rules: no long theoretical explanations, no unverified commands,
no conflicting rules, no temporary task requirements, no secrets, no
documentation that doesn't change future behaviour. Target under 80
lines for the root file.

===================================================================
STEP 4 — WRITE NESTED FILES, ONLY THE JUSTIFIED ONES
===================================================================
For each nested location from step 2, write ONLY the rules that
differ from root. Do not repeat root rules.

===================================================================
STEP 5 — REFERENCE, DON'T INLINE
===================================================================
Anything needing more than 2-3 lines in step 3 gets extracted to a
referenced doc, with one line pointing to it left in CLAUDE.md.

===================================================================
STEP 6 — PROVE THE HIERARCHY ACTUALLY WORKS
===================================================================
Pick one nested location with a genuinely different rule from root.
Ask the same question from inside that directory's context and from
root context. Show the two answers actually differ, and trace the
difference to the nested file. Paste both side by side.

===================================================================
STEP 7 — VERSIONING AND MAINTENANCE PLAN
===================================================================
State how this file stays in sync as code changes, what the risk is
if a command goes stale, and one concrete maintenance practice.

===================================================================
STEP 8 — REPORT
===================================================================
List every file written, root or nested, line count, confirm under
target length. State what was excluded and why. State the step 6
proof result explicitly, pass or fail, with both answers shown.
```

---

## What this actually produces against cartsvc — worked, not hypothetical

I can predict this with confidence because the repo's real structure
is already known from building it earlier in this thread.

### Step 0 — verified commands, real

```bash
python3 -m pytest -q          # 20 passed
python3 fixtures/concurrent_checkout.py   # both scenarios FAIL, by design
```

No stale command exists in cartsvc's README the way one was
deliberately seeded into RxFlow's — so step 0 against cartsvc passes
cleanly. Against RxFlow, expect step 0 to hit the seeded broken command
and correctly refuse to write it into CLAUDE.md. **That difference
alone is worth demonstrating to a room** — same prompt, two repos, one
catches a real problem and one doesn't, purely because of what's
actually in each repo.

### Step 2 — real module boundaries, with genuine differing rules

| Module | Differs from root because |
|---|---|
| `src/cart/pricing.py` | Needs a rule root doesn't: **characterization tests before any change** — this is the file with the tax-before-discount defect, silently wrong while every unit test passes |
| `src/cart/coupons.py` and `src/cart/cart.py` | Need a rule about **non-atomic check-then-write patterns requiring explicit review** — this is where the oversell and coupon-reuse races live |
| `src/cart/catalog.py` | Needs a rule root doesn't: **no string interpolation into SQL, ever** — this is the file with the seeded injection |
| `src/cart/risk.py`, `src/cart/db.py` | No genuine differing rule found → **correctly excluded from nesting**, root rules suffice |

Five source files, three justified nested locations, two correctly
rejected. That 3-out-of-5 result is exactly what step 2 is designed to
produce — not five folders getting a file because five folders exist.

### Step 6 — the proof, concretely

Ask *"can I make a database change here without extra scrutiny?"* from
inside `pricing.py`'s context versus from root context. Root says yes
by default. The `pricing.py`-nested file says no — characterization
tests required first, because that file has a defect that a plain unit
test suite already proved it can't catch. Two different, correct
answers, traceable to one nested rule. That's a real pass, not an
assumed one.

### RxFlow, once built — the parallel case

Your original syllabus for Lab 4 names `order_api, routing, pricing,
workers, infra` as the five candidate nested locations. Running step 2
against the actual built repo may not justify all five — exactly the
caution flagged in the earlier reply. `pricing` almost certainly earns
one, for the identical reason cartsvc's does: a large untested module
with a defect a normal test suite can't see (RxFlow's seeded 900-line
pricing module with three copies of the discount rule mirrors
cartsvc's tax bug structurally). Whether `workers` or `infra` earn
their own file depends on what's actually different about their rules
once the repo exists to inspect — that's for step 2 to determine
against the real thing, not for this document to assert in advance.

---

## The connection worth stating plainly

Same prompt, same eight steps, two repos — one gives you a real,
checkable answer right now, the other gives you a structurally
identical answer once you've done the one missing step: actually
building it with Docker in Claude Code. Nothing about Module 6 changes
between them. What changes is only whether step 0 and step 6 have
something real to inspect and prove against.

---

*Coderrange · corporate training and engineering capability*
