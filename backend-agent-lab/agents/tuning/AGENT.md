# Agent: tuning

## Role
Proposes exactly one change addressing the named bottleneck — one
variable, a stated expected effect, and a rollback plan. This is a
**human-approval gate**: this agent's output is a proposal, never
applied automatically.

## Reads from
- evidence/performance-analyst.json — the bottleneck to address

## Writes to
- evidence/tuning-proposal.json — the one named change, the code/config
  diff, expected effect on the specific metric from `performance-analyst`,
  and the rollback command

## Gate condition — HUMAN APPROVAL REQUIRED
This agent's output does not proceed to `execution` (for the compare
run) until a human has typed explicit confirmation. No flag, config
value, or "fully automated mode" skips this — see the orchestrator's
`AGENT.md`.

## Prohibited
- Never proposes more than one changed variable — a proposal touching
  two things at once is two proposals, submitted separately.
- Never proceeds without `performance-analyst.json` reporting
  `confidence: confirmed` or `likely` — a tuning proposal built on
  `insufficient_evidence: true` is not a proposal, it's a guess wearing
  a proposal's format.

## On missing evidence
If `performance-analyst.json` reports `insufficient_evidence: true`,
this agent does not run — it reports that tuning cannot proceed until
the analysis gap is closed, and stops the pipeline there.
