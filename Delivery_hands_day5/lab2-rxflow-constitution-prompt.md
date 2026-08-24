# Hands-on Lab 4 — RxFlow Engineering Constitution
## Run this once RxFlow is built and running in Claude Code

This lab only works against the real repo. If RxFlow hasn't been built
yet with the earlier build prompt (Docker required), build it first —
this prompt has nothing to inspect otherwise.

---

## The prompt

```
Role: build the durable engineering guidance hierarchy for this
repository — CLAUDE.md files that will be loaded on every future
session. This is the repository's engineering constitution, not a
one-off explanation.

===================================================================
STEP 0 — VERIFY BEFORE WRITING ANYTHING
===================================================================
Run the real build, test, lint, and type-check commands. Paste exact
output. If the README documents a command that fails, say so
explicitly — do not write it into any CLAUDE.md file, and do not
silently correct it without flagging that the README is wrong.

===================================================================
STEP 1 — JUSTIFY EACH OF THE FIVE CANDIDATE MODULES
===================================================================
The five candidates are: order_api, routing, pricing, workers, infra.

For each, inspect the actual code and state ONE thing:
  - what rule would this module need that the root file does NOT
    already cover?

If you cannot find a genuine differing rule for a module, say so
explicitly and do not create a nested file for it. A module getting
a CLAUDE.md file because it's in this list, not because it earned one,
is a mistake — report it as one if you find yourself about to make it.

Show as a table: module | differing rule found | justified (yes/no).

===================================================================
STEP 2 — WRITE THE ROOT CLAUDE.md
===================================================================
Verified commands from step 0. Architecture boundaries between the
five modules — stated as rules, from actually reading the imports
between them, not assumed from the module names. Security rules
covering what must never reach a log (this repo handles patient
prescriptions — be specific about which fields). Definition of done.

Under 80 lines. Reference docs/architecture.md and docs/code-review.md
by filename for anything longer — do not inline them.

===================================================================
STEP 3 — WRITE docs/architecture.md AND docs/code-review.md
===================================================================
architecture.md: the real module boundaries and data flow, in enough
detail that root CLAUDE.md's one-line reference to it is sufficient.

code-review.md: the actual PR review checklist for this repo — derived
from what step 0 and step 1 found, not generic best practice.

Both referenced from root CLAUDE.md by filename, not duplicated in it.

===================================================================
STEP 4 — WRITE THE NESTED FILES, ONLY THE JUSTIFIED ONES
===================================================================
For each module marked "yes" in step 1: write only the differing
rule(s). Do not repeat root content. If a module's differing rule
relates to a known seeded defect area (pricing is the obvious
candidate — large, untested, three copies of a discount rule), name
that specifically: "no behaviour change without a characterization
test first" is a real rule here, not boilerplate.

===================================================================
STEP 5 — PROVE IT IN THREE DIRECTORIES
===================================================================
Pick ONE question that a genuinely different answer should exist for
depending on location — for example: "can I merge a change to this
module without an additional review step beyond standard PR review?"

Ask it three times, from three different module contexts — at minimum
one that got a nested file and root itself, ideally three that
differ from each other. For each:
  - state which CLAUDE.md file(s) apply at that location
  - give the actual answer to the question
  - trace the answer to the specific line in the specific file that
    produced it

Present all three side by side. If two of the three give the same
answer, that is only acceptable if you can show their governing rule
is genuinely identical — not just that you forgot to check.

If none of your nested files produce a different answer from root
anywhere, the hierarchy has failed this lab's actual requirement —
go back to step 1, the justification was likely too generous.

===================================================================
STEP 6 — REPORT
===================================================================
List every file written: root, nested (with justification restated),
and the two referenced docs. Show the step 5 three-way proof in full,
not summarised. State plainly whether the hierarchy passed — meaning
at least one real difference was demonstrated and traced to a specific
file and line.
```

---

## What makes this lab's proof stricter than the general Module 6 prompt

**Three directories, not two.** The general prompt asks for one
nested-vs-root comparison. This lab specifically asks for three,
because RxFlow has five real candidate modules — a hierarchy that only
manages to differ in one place out of five candidates is a weak
result, even if technically passing. Three genuinely differing answers
is a stronger demonstration that the nesting was worth building at
all.

**Step 1 requires the participant to reject modules, not just accept
them.** Five names are given. The lab's actual test of understanding is
whether someone can look at `workers` or `infra` and honestly conclude
"no differing rule found here" rather than writing a file because the
lab handed them five names to fill in. A hierarchy where all five pass
justification is not automatically wrong, but it should be treated as
a result to double-check, not a default expectation.

**Step 5's failure condition is stated explicitly.** If nothing differs
across three directories, the prompt doesn't let that pass as "well,
we tried" — it sends the participant back to step 1. This mirrors the
earlier lesson from Module 6: an unproven hierarchy is not a smaller
version of success, it's a failure that happens to have files sitting
on disk.

---

*Coderrange · corporate training and engineering capability*
