# Hands-on Lab 5 — The Release-Readiness Skill
## Built to catch real problems, not to perform a checklist

The risk with a release-readiness Skill is that it becomes theater —
nine checkboxes that all say "OK" regardless of what's actually in the
diff. The prompt below is built to prevent that specifically: every
step requires evidence, and the proof step at the end uses a diff the
participant did not write, so there's no way to already know the
answer going in.

---

## Part 1 — Build the Skill

```
Role: build a release-readiness Skill for this repository. This will
be run before every merge, by people who did not write the change
being reviewed. It has to work on code nobody in the room has seen
before — including you, right now.

TRIGGER
State precisely when this fires: before merge, given a branch or diff
reference. State when it should NOT fire — e.g. a draft PR, a change
still marked work-in-progress.

===================================================================
THE NINE CHECKS — each needs a real finding, not a status word
===================================================================
For every check below, "OK" or "no issues" is not an acceptable
output on its own. State what you actually looked at and what you
found, even if the finding is "nothing concerning, and here is why
I'm confident of that."

1. IDENTIFY CHANGED SERVICES
   From the diff, not from the PR description. List every module
   touched. If the diff touches a module the PR description doesn't
   mention, flag that explicitly — undisclosed scope is itself a
   finding.

2. FIND AFFECTED TESTS
   Which existing tests exercise the changed code paths? Which
   changed code paths have NO existing test? The second list matters
   more than the first — untested changed code is the highest-risk
   category in any diff.

3. RUN FOCUSED VALIDATION
   Actually run the tests identified in step 2. Paste real output.
   Do not report "tests would pass" — run them.

4. CHECK API COMPATIBILITY AGAINST THE PREVIOUS OPENAPI SCHEMA
   Diff the current schema against what this branch would produce.
   Any removed field, changed type, or new required field is a
   breaking change — name it as one explicitly, don't soften it to
   "a small adjustment."

5. REVIEW ALEMBIC CHANGES
   If this diff includes a migration: does it have a working
   downgrade()? Does it match the model changes in the same diff, or
   could they drift apart? Has it been tested against a real
   database, or only asserted to work?

6. CHECK ERROR HANDLING
   For every new external call or new failure path in the diff: is
   there an explicit timeout? An explicit exception type caught, not
   a bare except? What happens to the caller if this fails?

7. VERIFY LOGS AND METRICS
   Does the diff log anything it shouldn't (PII, secrets, full
   payloads)? Does it remove or change a log/metric that something
   downstream might depend on? Both directions matter — adding a
   leak and silently removing observability are both findings.

8. REVIEW SECURITY RISK
   Anything touching auth, SQL construction, or a new input path from
   outside the system. Do not treat this as covered because check 4
   or 6 already ran — security risk needs its own explicit pass.

9. GENERATE THE STRUCTURED RELEASE REPORT
   Compile checks 1-8 into one report. Structure: summary verdict
   (ready / not ready / ready with conditions), then each check with
   its finding and severity (blocker / should-fix / informational).

===================================================================
VALIDATION AND FALLBACK
===================================================================
If any check cannot be completed — a test won't run, the previous
schema isn't available to diff against, a migration can't be tested
against a real database in this environment — the Skill must say so
explicitly in the report as "COULD NOT VERIFY: <reason>", not skip
the check silently and not guess at a plausible answer.

===================================================================
ERROR REPORTING
===================================================================
State what "honest failure" looks like for this Skill specifically:
not "something went wrong" but which of the nine checks failed, why,
and what the person running it should do before trusting the rest of
the report.
```

---

## Part 2 — Prove it, on a change the participant did not write

This is the part that actually tests whether the Skill works, not
whether it was built to spec.

**Setup, done by the instructor beforehand — the participant must not
see this step:**

```
Create a branch on RxFlow with a change that:
  - fixes one real thing correctly
  - simultaneously introduces one new, different problem — not the
    same category as the fix, so a checklist run on autopilot won't
    happen to catch it by coincidence

Do not comment on either. Do not name what the new problem is
anywhere the participant could see it.
```

**What the participant actually runs, in a fresh session, with no
memory of how this branch was built:**

```
Run the release-readiness Skill against this branch: <branch ref>

You did not write this change. Do not assume it is safe because it
claims to fix something. Run all nine checks for real — actual
commands, actual output, actual diffs against the schema and the
Alembic history.

Give me the structured report. If your verdict is "ready to merge,"
I will treat that as your professional judgement — be certain before
you say it.
```

---

## Why this design is more valuable to the coder than a checklist run

**"OK" is banned as a standalone answer.** A Skill that can report
"OK" without evidence is a Skill that will eventually report "OK" on
something that isn't. Forcing every check to produce a real finding —
even a confident "nothing found, and here's what I checked to be
sure" — means the coder using this Skill gets something they can
actually verify, not something they have to trust blindly.

**Check 2's inversion is the highest-value line in the whole prompt.**
Most release checklists ask "which tests pass." This one asks "which
changed code has NO test," and states plainly that the second list
matters more. That reframing is what actually protects a coder from
merging something dangerous — passing tests tell you nothing about
code the tests never touch.

**The proof step uses a diff with two independent problems, not one.**
If the planted defect is the only thing wrong, a lucky or lazy run of
the Skill can still stumble onto it. Two unrelated issues — a real fix
plus a new, different problem — means the Skill has to actually work
across all nine checks, not just get lucky on the one thing the
instructor cared about.

**The participant is told their verdict will be trusted.** That final
line — "I will treat that as your professional judgement" — is
deliberate. A release-readiness check run knowing nobody will act on
it produces a different quality of effort than one run knowing a real
merge decision rides on it. This is the same principle as a fire
drill versus a real fire: the second one gets your full attention.

**What a coder actually takes away from this lab:** not "I ran nine
checks." It's the felt experience of catching something real in code
someone else wrote, using a tool they built themselves — followed by
the sober realization, if the planted defect is missed, of exactly
what "OK" without evidence would have let through in production.

---

*Coderrange · corporate training and engineering capability*
