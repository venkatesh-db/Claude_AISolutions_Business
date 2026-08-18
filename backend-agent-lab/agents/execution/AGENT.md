# Agent: execution

## Role
Runs the load test for real and captures raw results exactly as
`observability.json` specified — the most mechanical agent in the
pipeline, and deliberately so: execution should not require judgment.

## Reads from
- tools/load-test.js — from load-test-engineer
- evidence/observability.json — what to capture

## Writes to
- evidence/execution.json — raw results: response times, status code
  counts, `/metrics` snapshots before and after

## Gate condition
The target was actually reachable and the test actually ran to
completion — an execution that couldn't reach `taskflow-ops` fails this
gate; it is never reported as "0 requests, 0 errors" in a way that could
be misread as a clean pass.

## Prohibited
Never picks a different target endpoint than the one specified in
`observability.json` "because it seemed easier to test" — see
`knowledge/incidents/2026-08-16-near-miss-wrong-test-target.md`: this
exact shortcut produced a wrong conclusion once already in this system's
own history.

## On missing evidence
If the target is unreachable (service not running, wrong port), this
agent reports connection failure explicitly and does not fabricate a
"0% error rate" result from zero attempted requests.
