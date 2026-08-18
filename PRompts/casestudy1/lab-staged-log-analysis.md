# Lab: Staged Log Analysis
## Evidence-first prompting, taught on a file participants can verify themselves

**Duration:** 45–60 minutes
**Evidence file:** `logs/api-2026-08-17.log` — 36,130 lines, 3.3 MB
**Prerequisite:** none. This is the first hands-on exercise of Day 1.

**Why this lab is first:** every claim the model makes here can be
checked with a single `grep -c`. Participants do not have to take the
instructor's word that hallucination happens. They see it, count it,
and catch it themselves.

---

## Part 1 — Run the weak prompt first (5 minutes)

Do this before teaching anything. It is the hook.

```
Look at logs/api-2026-08-17.log and tell me what went wrong.
```

Expect a fluent paragraph about database connection pool exhaustion.
It will probably be directionally right, contain no counts, and miss
the warning ramp entirely.

**Ask the room one question:** *how would you check any of that?*

There is no way to check it. That is the point. The answer is
unfalsifiable, which makes it unusable in a review, an incident report,
or a regulator conversation — regardless of whether it happens to be
correct.

---

## Part 2 — The strong prompt

Participants paste this and work through it stage by stage.

```
Work through this in stages. Stop after each and wait for me.

Task: our API started returning 500s yesterday evening. I do not
know why. I want to understand the pattern before anyone guesses
at a cause.

Evidence: logs/api-2026-08-17.log

1. UNDERSTAND — restate what I am asking, and what I am not.

2. INSPECT — read-only.
   - How many 500s, and in what time window?
   - Group them by endpoint and by error message.
   - Show the top 3 groups with counts.
   - Quote one real example line per group.
   - Also look at WARN and INFO lines, not only ERROR.
   - Mark each observation CONFIRMED (you counted it) or
     HYPOTHESIS (you inferred it).
   - State the exact command you used for each count.

3. PLAN — what you would investigate next, in what order, and why.
   Name what evidence you would need that you do not have.

Do not open any source code. Do not suggest a fix.
Stop at 3.
```

### The four moves, visible in this prompt

| Move | Where it appears |
|---|---|
| State the role and stakes | "before anyone guesses at a cause" |
| Give evidence, not description | a named file, not "customers are complaining" |
| Constrain the output shape | counts, groups, CONFIRMED / HYPOTHESIS, commands used |
| Forbid the shortcut | no source code, no fix, stop at 3 |

### Two lines that do most of the work

**"Also look at WARN and INFO lines, not only ERROR."**
Without this, most attempts grep only `ERROR` and miss the entire
lead-in. Teach it as a general habit: the failure is in the errors, the
cause is usually in what surrounds them.

**"State the exact command you used for each count."**
This converts every number into something a participant can re-run in
ten seconds. A model that cannot produce the command did not count —
it estimated.

---

## Part 3 — Verify (10 minutes, in pairs)

Participants re-run the counts themselves.

```bash
# total 500s
grep -c 'status=500' logs/api-2026-08-17.log

# by endpoint
grep 'status=500' logs/api-2026-08-17.log | grep -c '/orders'
grep 'status=500' logs/api-2026-08-17.log | grep -c '/pricing/quote'
grep 'status=500' logs/api-2026-08-17.log | grep -c '/labs/health'

# the dominant message
grep -c 'connection pool timeout' logs/api-2026-08-17.log

# window boundaries
grep 'status=500' logs/api-2026-08-17.log | head -1
grep 'status=500' logs/api-2026-08-17.log | tail -1

# what surrounds the incident
grep 'deploy complete' logs/api-2026-08-17.log
grep -c 'pool utilisation high' logs/api-2026-08-17.log
grep 'pool resized' logs/api-2026-08-17.log
```

---

## Answer key

Verified by running the commands above, not by inspection.

| Claim | Value |
|---|---|
| Total 500s | 1,847 |
| First error | 19:12:01 |
| Last error | 21:40:00 |
| Errors outside that window | none |
| `/orders` | 1,610 |
| `/pricing/quote` | 214 |
| `/labs/health` | 23 |
| Lines containing the pool timeout message | 1,767 |

### What is planted in the file

**A deploy at 19:08:41** — four minutes before the first error, version
`2026.08.17-r3`. Findable only by someone who looks outside the ERROR
lines.

**900 WARN lines from 19:04** showing pool utilisation climbing, with a
growing `waiting=` count. This is eight minutes *before* the first
error. The real story is in the warnings.

**A recovery line at 21:41:03** — oncall resized the pool from 20 to 60.
Explains why the errors stop, and confirms the diagnosis.

**The `/pricing` group is not homogeneous.** 150 are pool timeouts;
64 are `InvalidOperation: decimal conversion failed for discount_rate`
and have nothing to do with the incident. Reporting "214 pricing errors
caused by the pool" is an over-generalisation the counts disprove.

**No correlation IDs anywhere in the file.** Linking a `/pricing`
failure to a specific `/orders` failure is therefore impossible from
this evidence. Any such claim must be marked HYPOTHESIS. This is the
honest-uncertainty checkpoint, and the most valuable single finding in
the lab.

---

## Grading rubric

| Level | What it looks like |
|---|---|
| **Weak** | Names pool exhaustion. No counts. Only looked at ERROR lines. Misses the warning ramp and the deploy. |
| **Adequate** | Correct totals and window. Correct top-3 grouping. Marks the cross-endpoint causal link as HYPOTHESIS rather than asserting it. |
| **Strong** | All of the above, plus: finds the 19:04 warning ramp preceding the errors, spots the 19:08 deploy, separates the 64 decimal errors as unrelated, and states explicitly that no correlation ID exists so cross-endpoint causation cannot be established from this file. |

Grade on evidence quality, not on reaching a conclusion. A participant
who reports "I cannot determine causation from this file, here is what
I would need" has done better work than one who confidently names a
root cause.

---

## Discussion to close the lab (10 minutes)

**"What evidence do you not have?"**
Let the room answer. They will arrive at: request volume per minute,
pool size configuration history, and a deploy timeline correlated to
the errors. None of it is in the log.

That gap is not a debugging failure. It is an **observability gap**,
discovered through a debugging exercise. No correlation IDs means no
request can be traced across services — which is a design decision
someone made, and is now costing an incident.

**Bridge to the next module:** the fix for this is not a better prompt.
It is correlation IDs, structured logging, and request-volume metrics.
Prompting well told you what you were missing. It could not invent it.

---

## Instructor notes

**Run the weak prompt on the projector, not on laptops.** The room needs
to see the same fluent, uncheckable paragraph at the same moment.

**Do not reveal the planted deploy line.** Let one participant find it.
It changes the mood of the room when someone does.

**If a count comes back wrong,** stop everything and put it on the
screen. A live, verifiable hallucination is worth more than an hour of
theory about hallucination.

**Expect the loop to want to continue past stage 3.** Participants will
let it. Point out that they are now reviewing a conclusion instead of
evidence — which is exactly what the STOP was there to prevent.

---

*Coderrange · corporate training and engineering capability*
