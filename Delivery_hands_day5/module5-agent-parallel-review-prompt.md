# Module 8 — Sub-Agents, Parallel Review, Worktrees
## Parallel Release Review, applied to RxFlow

The value of this lab is not "run five agents at once." It's learning
when that's correct and when it's waste, and — the harder skill —
consolidating five outputs into one trustworthy decision instead of
handing a coder five opinions to sort out themselves.

---

## The prompt

Run against the Day 1 patch, or the release-readiness branch from
Lab 5.

```
Role: you are the PARENT agent coordinating a parallel release review.
You are accountable for the final decision — the sub-agents you spawn
are not.

===================================================================
STEP 1 — DECIDE IF FAN-OUT IS EVEN JUSTIFIED
===================================================================
Before spawning anything: is this change small and sequential enough
that one agent with full context would be faster and just as
reliable? State your reasoning either way.

Fan-out is justified only when the reviews genuinely don't depend on
each other's findings. If a security finding would change what the
performance reviewer should look at, they are not independent —
don't fan them out.

If you decide fan-out is NOT justified here, say so and do a single-
agent review instead. Do not fan out by default because this is a
"parallel review lab" — that would be exactly the unnecessary fan-out
this module warns against.

===================================================================
STEP 2 — IF JUSTIFIED, DEFINE BOUNDED TASKS FOR EACH SPECIALIST
===================================================================
For each of the six specialists you're using, write a bounded
instruction — not "review the code" but a specific, falsifiable
question each one is answering:

  REPOSITORY ANALYST
    What changed, structurally? Which modules, which boundaries
    crossed. Read-only, no opinion on whether the change is good.

  IMPLEMENTATION ENGINEER
    Does the code do what the PR description claims? Trace it, don't
    assume it from the diff alone.

  TEST ENGINEER
    Which changed paths have no test coverage? (Same inversion as
    Lab 5 — untested code matters more than passing tests.)

  SECURITY REVIEWER
    Auth, SQL construction, new external input paths only. Not a
    general code review — stay in this lane.

  PERFORMANCE REVIEWER
    Anything in the diff that could change latency or load under
    concurrency. Cite what specifically, not a general impression.

  DOCUMENTATION REVIEWER
    Does anything in this diff make existing docs, CLAUDE.md, or the
    OpenAPI schema inaccurate? Flag drift, don't just check presence.

Each agent gets ONLY its bounded question and the diff — not the
other five agents' instructions, and not your own reasoning about
what you expect to find. Contaminating their context with your
expectations defeats the purpose of independent review.

===================================================================
STEP 3 — GIT WORKTREE ISOLATION
===================================================================
State explicitly: are these agents operating on the same working
directory, or isolated worktrees? If shared, name the specific risk
(one agent's exploratory edit or checkout affecting what another
agent reads) and confirm each is read-only for this review. If any
agent needs to actually run something that could touch files, it
gets its own worktree — not a shared directory with a promise not to
interfere.

===================================================================
STEP 4 — RUN, THEN CONSOLIDATE — DO NOT JUST FORWARD
===================================================================
Once all six return, you as parent agent must:

  1. Identify duplicate findings — the same real issue reported by
     more than one specialist in different words. Merge them, cite
     both sources.
  2. Identify CONTRADICTORY findings — two specialists disagreeing.
     Do not average them or pick one arbitrarily. State the
     contradiction explicitly and say what would resolve it.
  3. REJECT unsupported claims. If a specialist asserts something
     without a file/line citation, it does not go into the final
     report as a finding — it goes into a separate "unverified,
     needs follow-up" section, clearly marked as different from a
     confirmed finding.
  4. Order everything that survives by actual severity — blocker,
     should-fix, informational. Six specialists each calling their
     own finding "critical" does not mean you have six blockers.

===================================================================
STEP 5 — ONE RELEASE DECISION
===================================================================
The coder using this needs ONE verdict, not six reports stapled
together: merge, do not merge, or merge with named follow-ups. State
it plainly, backed by the consolidated findings from step 4 — not by
restating what each specialist said.

===================================================================
STEP 6 — WHAT YOU, THE PARENT, ARE ACCOUNTABLE FOR
===================================================================
State plainly: if this release decision turns out wrong, the fault is
not "the security reviewer missed it" — you are the parent agent, you
made the call on what to trust, reject, and merge into one decision.
Name what you would have needed to be more confident, if anything.
```

---

## Steering and cancelling mid-flight — the practical addition

Add this as a standing instruction, not a separate run:

```
If, while any specialist is running, you notice its bounded question
was wrong — too broad, missing context it needed, or chasing
something already resolved by another specialist's early finding —
cancel it and re-issue a corrected bounded task rather than letting
it complete and discarding the output afterward. Wasted agent time
noticed early is cheap. Wasted agent time discovered after
completion is not.
```

---

## Why this design is more valuable to a coder than "run six agents"

**Step 1 can produce "don't fan out" as a valid answer**, and that's
the actual teaching point of the whole module. A coder who learns to
fan out by default has learned the expensive habit, not the correct
one. The real skill is knowing when *not* to.

**Step 2 forces falsifiable questions, not open-ended reviews.** "Review
the code" from six agents produces six overlapping essays. A bounded
question like "which changed paths have no test coverage" produces a
specific, checkable list — the same evidence discipline running
through every other lab in this course, applied to how sub-agent
instructions get written.

**Step 4 is where the actual value to a coder lives.** Not in having
six opinions — in having one person (the parent agent) do the
unglamorous work of merging duplicates, refusing to pass along
unsupported claims, and resolving contradictions instead of averaging
them. A coder who receives six raw reports has more work than one who
never asked for a parallel review at all. A coder who receives one
clean, severity-ordered verdict has genuinely saved time.

**Step 6 closes the accountability gap that makes fan-out feel
consequence-free.** Without it, a wrong release decision has six
possible people to blame and nobody actually responsible. Naming the
parent agent as accountable — the same way a human tech lead who
delegates a review is still accountable for the merge decision —
is what makes this pattern trustworthy enough to use on a real
release, not just an interesting lab exercise.

---
