# Module 5 — Test-Driven Implementation Prompt
## The twelve-step workflow, with testing strategy selection built in

---

## Why one universal prompt doesn't work here

Nine testing strategies are listed in the module. No single defect
needs all nine. A prompt that tries to invoke every strategy on every
bug produces bloat — a `hypothesis` property test on a static routing
table, or a `testcontainers` integration test on a pure pricing
function, wastes time and teaches the wrong instinct.

**The actual skill Module 5 is teaching is selection, not coverage.**
So the prompt below has two parts: the twelve-step scaffold, which is
constant, and a strategy-selection block, which participants fill in
themselves at step 7 based on what the defect actually is.

---

## The strategy-to-defect map

Use this to check a participant's step 7 choice, or hand it to them
before they start.

| Testing strategy | Fits which kind of defect | RxFlow example |
|---|---|---|
| Fixtures, factories, deterministic builders | Every test, always — this is baseline hygiene | All ten |
| Table-driven / `parametrize` | Many similar inputs, one code path | Prescription clamping (defect 2) — sweep cylinder/axis boundary values |
| Property-based (`hypothesis`) | An invariant that must hold for *all* inputs, not specific ones | Prescription range validation (defect 2) — "no accepted value is ever outside physical grinding limits" |
| Concurrency (`asyncio` / threads) | Two requests racing for the same resource | Duplicate lens job (defect 1), Redis counter drift (defect 5) |
| Integration (`testcontainers`) | Real Postgres/Redis behaviour that a mock would hide | Transaction boundaries, Redis atomicity (defects 1, 5) |
| Fault injection on the lab connector | External call failure, timeout, retry | Celery retry amplification (defect 4) |
| Contract tests against OpenAPI schema | A response shape or status code claim | Lab-override auth (defect 7) — does 401 actually appear in the schema |
| Characterization tests | Legacy code with no coverage, about to be touched | Pricing module (defect 8) — pin behaviour before deduplicating the discount rule |
| Performance regression assertions | A fix that could silently slow the hot path | Idempotency check added to order creation (defect 1) |

**The instruction to give participants:** before writing any test, name
which strategy fits and say why the others don't. Wrong strategy
selection is itself gradable — a characterization test on a
concurrency bug, or a property test on a static routing table, is a
finding worth catching before code gets written.

---






## The prompt

Fill in the `<DEFECT>` block per exercise. Template below is populated
for defect 1 (duplicate lens job) as a worked example — swap it for
any of the other nine.

```
Work through this in twelve stages. Stop after stage 6 and after
stage 8, and wait for me. Continue through the rest automatically
once approved.

DEFECT
<Duplicate lens job created when an optician retries a slow submit.
Approved task contract from Lab 2 is attached below.>

CONSTRAINTS
- Minimal patch only. No refactor beyond what the fix requires.
- No float in money paths, no PII in logs, no new outbound call
  without an explicit timeout — repo-wide non-negotiables.
- Every claim in every stage needs file and line range, marked
  CONFIRMED or HYPOTHESIS.

STAGE 1 — INSPECT THE ISSUE
Restate the defect in your own words. What is being asked, and what
is explicitly out of scope.

STAGE 2 — ESTABLISH A CLEAN, GREEN BASELINE
Run the full test suite now, before touching anything. Paste the real
output. If anything is already failing, stop and tell me — do not
attribute a pre-existing failure to this defect.

STAGE 3 — REPRODUCE THE PROBLEM DETERMINISTICALLY
Write a script or test that triggers the defect on demand. Run it
3 times. Paste all three outputs. It must fail 3/3 before you proceed.
If it does not, say what you changed and try again — do not continue
on a flaky reproduction.

STAGE 4 — IDENTIFY THE FAILING CODE PATH
Trace the exact path from entry point to the point of failure.
File and line for every step.

STAGE 5 — FORM A ROOT-CAUSE HYPOTHESIS
State the hypothesis in one sentence. What observation would prove it
false?

STAGE 6 — VERIFY THE HYPOTHESIS WITH EVIDENCE
Confirm or refute the hypothesis against the reproduction from stage 3
and the trace from stage 4. If refuted, return to stage 5 — do not
patch around a hypothesis you have not verified.

STOP. I will approve the diagnosis before you write any test or code.

--- after my approval ---

STAGE 7 — ADD A FAILING REGRESSION TEST
First: name which testing strategy from the list below fits this
defect, and say in one sentence why the others do not.

  fixtures/builders · table-driven/parametrize · property-based
  (hypothesis) · concurrency (asyncio/threads) · integration
  (testcontainers) · fault injection · contract test (OpenAPI) ·
  characterization test · performance regression

Then write the test. Run it. Show me it FAILING against current code
before any fix exists. Paste the output.

STAGE 8 — IMPLEMENT THE SMALLEST SAFE PATCH
The minimal change that makes the stage 7 test pass. Nothing else.

STOP. I will approve the diff before you run broader validation.

--- after my approval ---

STAGE 9 — RUN FOCUSED TESTS
The stage 7 test now passes. Paste real output. The stage 3
reproduction now passes 3/3. Paste all three runs.

STAGE 10 — RUN BROADER REGRESSION TESTS
Full suite. Paste real output. If anything unrelated now fails, stop
and report it — do not silently patch a second issue mid-flow.

STAGE 11 — REVIEW THE FINAL DIFF LINE BY LINE
Walk your own diff as if reviewing someone else's PR. What would a
reviewer flag? Be specific — do not write "looks good."

STAGE 12 — DOCUMENT EVIDENCE AND REMAINING RISK
Summarise: what was proven (with citations), what was assumed, what
remains unverified, and what would need to happen for this fix to be
safely rolled back.

Report format for the final message only: commands run, exact output,
files changed, remaining risk.
```

---

## Why the two STOP points are placed where they are, not elsewhere

**After stage 6, before stage 7.** This is the diagnosis gate. Once a
test gets written, the model is committed to a specific fix shape.
Catching a wrong root cause here costs one message. Catching it after
stage 8 costs a diff you have to unwind.

**After stage 8, before stage 9.** This is the same plan-then-implement
boundary from Day 1, applied a second time inside a single defect. The
patch exists but hasn't been validated broadly yet — the cheapest point
to say "this touches more than it should" is before the full suite
runs, not after.

**No stop between 9 and 12.** Once the patch is approved and passing,
validation, review, and documentation are mechanical enough to run
without a human gate every step. Two approval points per defect is the
right density — more than that and participants spend the lab
approving instead of doing.

---

## Worked example of the stage 7 strategy call, for defect 1

A participant might reasonably reach for `testcontainers` here, since
the bug involves a real database. **That's the wrong first answer.**
The defect reproduces with SQLite and threading — no real Postgres
behaviour is load-bearing to the bug itself. `testcontainers` becomes
relevant only if the eventual fix (a unique constraint, say) needs to
be verified against real Postgres constraint-violation semantics that
SQLite doesn't faithfully emulate.

The correct stage-7 answer is **concurrency (asyncio/threads)** for the
regression test itself, with a note that **integration (testcontainers)**
may be needed later specifically to validate the constraint behaves
identically against real Postgres before merge. That two-part answer —
what to use now, what to add before shipping — is what separates a
strong stage 7 from an adequate one.

---

## Grading the strategy selection, not just the test

| Level | What it looks like |
|---|---|
| Weak | Writes a test without naming a strategy. Or picks one that happens to pass without addressing why it fits. |
| Adequate | Names the correct primary strategy and gives a real reason the others don't fit. |
| Strong | Names the primary strategy, correctly identifies a secondary strategy needed before merge (as in the worked example above), and the reasoning for both would hold up if a reviewer asked "why this and not that." |

---

## One-line versions for the other nine defects, if you want to run this across the whole set

| # | Defect | Primary strategy at stage 7 |
|---|---|---|
| 2 | Prescription silently clamps out-of-range values | property-based (hypothesis) — the invariant is "no output value is ever outside grindable range," which table-driven tests can spot-check but not prove |
| 3 | Lab routing ignores live capacity | table-driven/parametrize — a fixed set of capacity scenarios, not an infinite input space |
| 4 | Celery retry amplifies load 3x | fault injection — must simulate the connector timeout to see the amplification |
| 5 | Redis in-flight counter drifts | concurrency + integration (testcontainers) — the drift is a real-Redis atomicity property, not reproducible against a mock |
| 6 | PII reaches logs | contract test — assert the log schema/fields never contain the flagged keys, run on every log call in the module |
| 7 | Lab-override endpoint has no auth check | contract test against OpenAPI — the schema should declare a 401 path that the code doesn't enforce |
| 8 | 900-line pricing module, no tests | characterization tests, first, before anything else touches the file |
| 9 | Alembic revision with no downgrade | integration (testcontainers) — apply and downgrade against a real Postgres to prove the migration path |
| 10 | SQL injection via f-strings | fault injection — feed the malicious input, assert it does not affect the query |

---

*Coderrange · corporate training and engineering capability*
