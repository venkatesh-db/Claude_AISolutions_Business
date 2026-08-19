# Prompt Playbook for Backend Developers
## Twelve prompts for the work you actually do

Copy these. Change the file names. That is the whole instruction.

**The four moves, in every prompt below:** state the stakes · give
evidence, not description · constrain the output shape · forbid the
shortcut you know it will take.

**The one habit that matters more than any prompt:** when it names a
file and line, open it. Ten seconds. If that one is real, the rest
probably is.

---

## Contents

| # | When you reach for it |
|---|---|
| 1 | You inherited a repo and have no idea what it does |
| 2 | A bug report arrived and you cannot reproduce it |
| 3 | You reproduced it and want the root cause, not a patch |
| 4 | You are ready to fix it |
| 5 | Someone's PR is waiting on you |
| 6 | Legacy code with no tests, and you must change it |
| 7 | "It feels slow" and you need a number |
| 8 | Production is down right now |
| 9 | You are designing a new endpoint |
| 10 | A dependency or framework upgrade |
| 11 | You are staring at a log file |
| 12 | End of session, before you close the thread |

---

## 1 · Understand an unfamiliar repository

```
Read-only. Do not modify anything.

I have never seen this repository. Give me a map I can act on.

Cover:
  - what each module is responsible for, one line each
  - the data model: tables, columns, constraints
  - every place a database connection or transaction is opened
  - all outbound calls and their timeout behaviour
  - what the test suite asserts, and what it does not
  - the three files I should read first, and why

Every claim needs a file and line range. Mark each CONFIRMED
(you read it) or HYPOTHESIS (you inferred it).

End with: what you did not open, and what you are unsure about.
```

**Why it works:** "what the test suite does not assert" surfaces more
than any positive question. So does "what you did not open" — a model
that read 8 of 40 files and says so is more useful than one that
answers about all 40.

---

## 2 · Turn a vague bug report into a reproduction

```
Read-only. Do not fix anything.

Bug report, verbatim: "<paste it>"
Evidence: <log file / trace / screenshot path>

I cannot reproduce this. Help me build a reproduction.

1. List every assumption in that bug report that has not been verified.
2. From the code, name the conditions that must hold for this symptom
   to occur — timing, data state, concurrency, config.
3. Give me the smallest script or test that would trigger it.
4. Tell me what evidence I would need to confirm the reproduction is
   the same failure the customer hit, not a different one that looks
   the same.

Do not propose a fix.
```

**Why it works:** step 4 is the one people skip. A reproduction that
produces a similar symptom by a different route sends you to the wrong
root cause with full confidence.

---

## 3 · Find the root cause

```
Read-only. Do not fix anything.

Symptom: <one line>
Reproduction: <command or test that triggers it>
Evidence: <files>

Trace the full path from entry to the point of failure.

For each step give:
  - file and line
  - what it reads or writes
  - the system state at that moment
  - whether anything else could interleave here

Then list every candidate cause, each marked CONFIRMED or HYPOTHESIS.

If two causes could both produce this symptom, say so and tell me what
would distinguish them. Do not choose for me.

Do not propose a fix. Do not write code.
```

**Why it works:** "do not choose for me" fights the model's pull toward
decisiveness. When two causes are genuinely indistinguishable from the
evidence, being told that is the finding.

---

## 4 · Implement the fix

```
Approved. Constraints:

- Smallest change that fixes the identified cause.
- Do not refactor anything you are not fixing.
- Do not change public signatures without telling me first.
- <domain rules: no float in money paths, no PII in logs, etc>

1. Write the failing test FIRST. Show me it failing before you patch.
2. Then the minimal patch.
3. Run the full suite. Paste actual output, not a summary.
4. Show me the diff and tell me what a reviewer would object to.
5. Report: commands run, files changed, what you could not verify.
```

**Why it works:** "show me it failing first" is the difference between a
test that proves the fix and a test written afterwards that passes for
reasons nobody checked.

---

## 5 · Review someone else's PR

**Use a fresh session.** A thread that helped write the code will agree
with it.

```
Read-only. You did not write this change. Review it for merge.

Diff: git diff main..<branch>

Review in this order:
  1. Correctness — does it do what the description claims? Name the
     case it still gets wrong, if any.
  2. Coverage — is there a test that fails without this change?
  3. Security — anything touching SQL, auth, logging, or personal data
     in the changed files or their immediate callers?
  4. Blast radius — what else calls the changed functions?
  5. Data — what happens to records already in the state this bug created?

For each finding: file, line, severity (blocker / should-fix / nit),
and what you would need to confirm it.

End with one line: merge, or do not merge, and why.

Do not fix anything. Do not soften findings.
```

**Why it works:** item 5 is the one engineers forget. A fix prevents new
bad records; it says nothing about the ones already written.

---

## 6 · Change legacy code with no tests

```
Read-only, then characterization tests only.

<module> has no coverage and I need to change it. Behaviour must not
change as a side effect.

1. Enumerate every distinct branch with file and line. Do not judge
   quality.
2. For each branch, propose one characterization test that pins CURRENT
   behaviour — including behaviour you believe is wrong.
3. Stop. Do not refactor. Do not deduplicate.

If two code paths that look equivalent actually differ, list the inputs
where they diverge. Do not decide which is correct.
```

**Why it works:** "pin behaviour you believe is wrong" is deliberate.
Models want to fix things while writing tests, which destroys the safety
net before you have built it.

---

## 7 · Turn "it feels slow" into a number

```
Read-only.

Complaint: <endpoint or job> feels slow.
Evidence: <trace / timing log / profile output, if any>

1. From the code, list every operation on this path that could take
   more than 10ms: queries, network calls, serialisation, loops over
   result sets.
2. For each: file, line, and what determines its cost (row count,
   payload size, retry policy).
3. Identify anything inside a loop that should be outside it, and any
   query pattern that scales with result count.
4. Tell me what I should measure first, and the exact command or
   instrumentation to measure it.

Do not optimise anything. I want a measurement plan, not a patch.
```

**Why it works:** step 4 prevents the most common waste in performance
work — optimising the thing that was easiest to see rather than the
thing that dominates.

---

## 8 · Production incident

```
Production incident. I need structure, not speed.

Symptom: <what users see>
Started: <time>
Evidence: <logs, dashboards, recent deploys>

1. What changed near the start time? Check deploys, config, traffic,
   dependencies. Cite what you actually looked at.
2. From the evidence only, what is CONFIRMED about the failure?
3. What are the candidate causes, ordered by how quickly each could be
   ruled in or out?
4. For the top candidate: what is the fastest safe check?
5. Is there a mitigation that does not require knowing the cause —
   rollback, feature flag, capacity, rate limit?

Answer 5 first if the answer is yes.

Do not change anything.
```

**Why it works:** "answer 5 first" reflects incident reality. Stopping
the bleeding beats understanding the wound. The model naturally
gravitates to diagnosis; this forces mitigation to the front.

---

## 9 · Design a new endpoint

```
Contract first. No implementation yet.

Requirement: <what it must do>
Existing conventions: <point at 2-3 similar endpoints in the repo>

Propose the contract:
  - request and response schemas, with types and required fields
  - every error case and its status code
  - idempotency behaviour — what happens on a retry?
  - pagination, if the response can grow
  - authorisation: who can call this, checked where?
  - what happens under partial failure

Match the conventions in the files I pointed at. Where you deviate,
say why.

List what I have not specified that you would have to guess. Do not
guess. Ask.

Do not write the implementation.
```

**Why it works:** "list what I have not specified — do not guess" is
where most API design bugs come from. The retry question alone prevents
a whole class of duplicate-record defects.

---

## 10 · Dependency or framework upgrade

```
Behaviour-preserving migration. Plan only.

Upgrade: <library> from <old> to <new>

1. What in this repo actually uses it? File and line for each usage.
2. Which usages are affected by breaking changes between these
   versions? Mark CONFIRMED (you checked the changelog or the code) or
   HYPOTHESIS.
3. What behaviour is currently untested and would change silently?
4. Propose the order: pin behaviour with characterization tests →
   pilot on one module → batch the rest → verify.
5. What is the rollback if this goes wrong after merge?

Success is zero behaviour change with evidence, not a fast diff.

Do not start the migration.
```

**Why it works:** step 3 is the risk. Breaking changes you know about
are easy. Silent behaviour changes in untested code are what break
production three weeks later.

---

## 11 · Read a log file

```
Read-only.

Evidence: <log file>

1. How many errors, and in what time window?
2. Group them by endpoint and by message. Top 3 with counts.
3. Quote one real line per group.
4. Look at WARN and INFO lines too, not only ERROR. What happens
   immediately before the first error?
5. State the exact command you used for each count.

Mark each observation CONFIRMED (you counted it) or HYPOTHESIS.

Then: what evidence would you need that this file does not contain?
```

**Why it works:** point 4 finds the cause. Errors are the symptom;
warnings usually start earlier. Point 5 makes every number checkable —
run one of the commands yourself and compare.

---

## 12 · Close a session cleanly

```
Summarise this session for a fresh thread. Include:
  - what we established as fact, with file and line
  - what we decided, and what we explicitly rejected and why
  - what is still unverified
  - the exact next step

Keep it under 15 lines. I will paste this into a new conversation.
```

**Why it works:** the model has no memory between threads. This is your
manual save. And anything you find yourself writing in this summary
*twice* belongs in `CLAUDE.md` instead — that is the difference between
a handoff and a standard.

---

## The prohibitions worth memorising

Six phrases that prevent most bad output.

| Phrase | Stops |
|---|---|
| `Read-only. Do not modify any file.` | Editing before diagnosing |
| `Do not propose a fix.` | Skipping to a solution |
| `Mark each CONFIRMED or HYPOTHESIS.` | Inference dressed as fact |
| `Show me it failing first.` | Tests written to pass |
| `Paste actual output, not a summary.` | Fabricated test results |
| `Do not choose for me.` | False decisiveness on ambiguity |

---

## Three checks, every time

**Open one thing it named.** It said line 47 — go look at line 47.

**Ask how it got a number.** Then run the same command yourself.

**Mention something fake.** Ask about a file that does not exist. If it
explains the file, stop trusting everything else in that session.

---

## What belongs in CLAUDE.md instead

If you type it more than twice, it is not a prompt — it is a standard.

```markdown
## Build and test  (verified <date>)
  <exact commands>

## Non-negotiable
- Never log personal data. Use the reference ID.
- Every migration needs a working rollback.
- Every defect fix ships with a test that fails without the fix.
- New outbound calls need an explicit timeout and retry policy.

## Report format
End every task with: commands run, exact output, files changed,
and anything you could not verify.
```

That file loads on every request, for every engineer, in every session.
Keep it short and operational — it competes for the same context as the
code you want it thinking about.

---

*Coderrange · corporate training and engineering capability*
