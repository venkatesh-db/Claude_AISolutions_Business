# Two Worked Examples — SSE and Principal Architect
## Same discipline, deliberately different outcomes

The point of this pair is to show the classification is not generic.
Run the identical eight-step prompt against two different roles and
the folder that comes out should look nothing alike. If it looks the
same, one of the two runs was done carelessly.

**Both examples below use assumed role details, clearly marked.**
Before either goes into real use, replace the assumptions with your
actual title, reporting line, and daily "done" criteria — that
substitution changes real answers in Step 1, not just cosmetic detail.

---

# Example 1 — SSE

**Assumption flagged:** SSE is treated here as *Solutions/Support
Systems Engineer* — the person who triages production and customer
issues, confirms root cause, and hands off to engineering. If your
SSE means something else (Sales Systems Engineer, Site Systems
Engineer), the classification below will be wrong in places, not just
mislabeled — re-run Step 1 with the correct definition before trusting
any of Steps 2-7.

**Domain:** retail commerce, cart-service (from earlier in this
thread — substitute your real system).

## STEP 1 — Classification

| Need | Mechanism | Why |
|---|---|---|
| Which system owns which failure type | CLAUDE.md fact | Stable, rarely changes |
| Escalation contacts per failure category | CLAUDE.md fact | Same reasoning |
| Draft customer status update | Slash command | Same shape, order ID + status vary |
| Ticket-ready escalation handoff | Slash command | Same shape, content varies |
| "Why did this specific checkout fail" | Skill | Multi-step, judgement at each stage |
| Live order status lookup | MCP server | Needs real system outside repo |
| Nightly stuck-order check | Tested at Step 7 | Resolves to scheduled read-only report, not orchestrator |

**Character of this role's work:** mostly *reactive* — something
breaks, you're told, you investigate and hand off. The tooling
reflects that: commands for communicating status, one Skill for
diagnosis, an MCP connection for evidence.

## STEP 2 — CLAUDE.md (SSE)

```markdown
## Role
Solutions/Support Systems Engineer, Commerce Platform. Triage
production and customer-reported checkout issues, confirm root cause
with evidence, hand off to engineering or resolve if it matches a
known pattern.

## Escalation ownership
- Stock/oversell → Fulfilment on-call
- Coupon/pricing → Commerce Platform (this team)
- Payment failures → Payments team, confirm reached them only
- Fraud holds → Risk team, explain score, do not override

## Non-negotiable
- Never invent an order ID or assume account state — check or ask
- Every fact about a specific case cites its source
- Ambiguous evidence stays reported as ambiguous, never picked-and-presented

## Report format
Asked / checked (with sources) / found (CONFIRMED or HYPOTHESIS) /
unknown / next action
```

## STEP 3 — Slash commands (SSE)

`/status-update` · `/escalation-summary` · `/known-pattern-check` ·
`/eod-queue-report` — as built in the prior worked example. These
hold up regardless of exact SSE definition, because "communicate
status" and "hand off with evidence" are close to universal for any
triage-facing role.

## STEP 4 — Skill (SSE)

`checkout-failure-investigation` — as built previously. This is the
one piece most sensitive to the SSE-definition assumption: if your
actual role doesn't do hands-on technical triage, this Skill may not
exist at all, and the real Step 1 candidate would be something else
entirely (e.g. "summarise a sales technical requirement" if SSE means
Sales Systems Engineer).

## STEP 7 — Orchestrator check (SSE)

No orchestrator. One candidate (nightly stuck-order check) resolves
to a scheduled read-only report, as established previously.

**What defines this role's output shape:** heavy on commands and one
Skill, light on everything else. Reactive, evidence-gathering,
handoff-oriented work rarely needs an MCP server beyond one read-only
connection, and essentially never needs an orchestrator, because a
human is always the one deciding what to do with a diagnosis.

---

# Example 2 — Principal Architect

**Assumption flagged:** treated here as the role responsible for
cross-team technical direction, design review, and standards — not
hands-on incident triage. If your Principal Architect role is closer
to "senior IC who also gets paged," blend this with Example 1 rather
than using either alone.

**Domain:** same retail commerce platform, architecture layer —
covers cart-service, risk-service, fulfilment-service as a system,
not any one incident.

## STEP 1 — Classification

| Need | Mechanism | Why |
|---|---|---|
| Architecture principles this org has agreed on | CLAUDE.md fact | Stable, referenced constantly |
| Service boundaries and who owns what | CLAUDE.md fact | Same |
| Draft an RFC from a rough proposal | Slash command | Same shape, content varies |
| Summarise a design review into decisions + open questions | Slash command | Same shape every time |
| "Does this proposed change violate an existing boundary or pattern" | Skill | Judgement — requires reading the proposal against multiple standing documents and reasoning about tradeoffs |
| "What is the actual current dependency graph across these services" | Skill | Judgement — requires tracing real code, not just reading a diagram someone drew once |
| Pull real deployment/ownership data across repos | MCP server | Needs systems (CI, service catalog) outside any one repo |
| Continuously flag architecture drift as code merges | Tested at Step 7 | Real orchestrator candidate — see below |

**Character of this role's work:** mostly *evaluative and preventive*
— reviewing proposals against standards, tracing how things actually
connect versus how they're documented to connect, catching drift
before it compounds. Very different shape from SSE's reactive
triage.

## STEP 2 — CLAUDE.md (Principal Architect)

```markdown
## Role
Principal Architect, Commerce Platform. Own cross-service technical
direction. Review proposals against agreed boundaries. Do not approve
by default — silence is not agreement.

## Standing architectural facts
- cart-service owns cart, checkout, pricing, coupons — nothing else
  may write to its tables directly
- risk-service is called synchronously at checkout; any proposal to
  make it async needs explicit sign-off, not assumed
- fulfilment-service is the source of truth for stock; cart-service
  must never cache stock counts past request scope

## Non-negotiable
- Never state a service boundary from memory — verify against the
  current repo, boundaries drift and documentation lags reality
- Distinguish "this is documented policy" from "this is how it
  happens to work today" — these are not the same claim
- Every architectural claim cites the actual file/config it came from,
  not the design doc, unless the design doc is what's being reviewed

## Report format
Proposal or question / what was checked against (docs vs live code,
named separately) / where they agree / where they diverge / recommendation
```

**Note the difference from the SSE file:** this CLAUDE.md spends real
weight on "documentation vs reality" because that gap is the
architect's actual daily risk — for an SSE, the risk is inventing
facts about one customer's account; for an architect, it's trusting a
design doc that no longer matches the code.

## STEP 3 — Slash commands (Principal Architect)

`/draft-rfc` — turn a rough proposal into RFC format with sections for
context, options considered, tradeoffs, recommendation.

`/review-summary` — after a design review meeting, turn notes into
decisions made, open questions, and owners for each.

`/boundary-check` — given a proposed change, check it against the
standing architectural facts in CLAUDE.md and flag any that appear
violated, citing the specific fact.

## STEP 4 — Skills (Principal Architect)

**`design-proposal-review`**
- Trigger: a new RFC or proposal needs review
- Steps: read the proposal, identify every service boundary it
  touches, check each against CLAUDE.md's standing facts *and*
  against the actual current code (not just the docs — that
  distinction from the CLAUDE.md rules applies here directly),
  identify tradeoffs the proposal didn't surface, form a
  recommendation
- Stop-and-ask point: if the proposal touches a boundary not yet
  documented in CLAUDE.md at all — that's a gap in the standing
  knowledge, not something to reason about from scratch each time
- Done: a review ready to paste into `/review-summary` format

**`dependency-graph-trace`**
- Trigger: "what actually depends on what" needs answering for real,
  not from a diagram
- Steps: trace actual imports/calls across the named services, build
  the real graph, compare it against any documented version, flag
  every place they diverge
- Stop-and-ask point: if tracing requires access to a repo not
  currently available — name exactly which one, don't estimate
- Done: a diff between documented and actual dependencies, with
  citations for the actual side

## STEP 5 — MCP requirement (Principal Architect)

**`service-catalog-readonly`**
- Tools: `get_service_owner(service)`, `get_deployment_history(service)`,
  `get_dependency_declarations(service)` — pulled from CI/service
  catalog, not from any single repo
- Read-only, consumed by `dependency-graph-trace` above
- Why this one and not more: an architect needs to know what's
  *actually* deployed and owned, which no single repo's CLAUDE.md can
  tell you — this is a genuinely cross-repo need, unlike most SSE
  needs which stay inside one system

## STEP 7 — Orchestrator check (Principal Architect)

This is the one role of the two where a real candidate survives.

**Candidate: continuous architecture drift detection.**

Testing honestly against the rung-6 question — must this run
unattended, with nobody available to approve each step:

- The trigger is real and continuous: every merge across every
  service, not something an architect reviews manually at that
  frequency.
- The action is still fundamentally a flag, not a write — "this merge
  appears to violate the cart-service boundary rule, flagging for
  review" is read-only in effect even though it's triggered
  automatically.
- **This is closer to a genuine orchestrator need than the SSE
  example produced**, because the trigger frequency (every merge,
  across many repos) genuinely cannot be a human remembering to run a
  command — but it should still stop short of write access. It
  flags and notifies; it never blocks a merge or edits code itself
  without a human approving that specific escalation.

**Honest answer: partially yes, scoped narrowly.** Build it as a
scheduled/event-triggered check with strictly read-only reasoning and
notification output — not as a system with any write authority. If it
ever needs to auto-block a merge, that crosses into a write action and
needs its own explicit approval-gate design, same rule as the SSE
example's MCP server.

---

## Why these two came out different, and what that proves

SSE: four commands, one Skill, one narrow MCP connection, no
orchestrator. Reactive, single-system, human-decides-every-time.

Principal Architect: three commands, two Skills, one cross-repo MCP
connection, and one genuinely justified — but narrowly scoped —
orchestrator candidate. Evaluative, cross-system, and the one place
where "nobody can manually trigger this at the frequency required" is
actually true rather than assumed.

**The test this pair passes:** two different roles run through the
identical eight-step process and produced structurally different
folders, for reasons traceable to the actual nature of each role's
work — not because one person likes agents more than the other. If a
second attempt at either role converged on a similar-looking folder to
the wrong role's output, that would be the signal the classification
was done carelessly rather than honestly.

---
