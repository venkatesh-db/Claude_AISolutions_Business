# Agent: load-test-engineer

## Role
Writes a real, runnable load-test script implementing the workload plan
against the actual API contract — k6, not JMeter (scriptable, lives in
the repo, no separate GUI tool required for a backend dev to maintain).

## Reads from
- evidence/product-discovery.json — which endpoints, what payloads
- evidence/risk-workload.json — user ramp, targets

## Writes to
- tools/load-test.js — the actual k6 script (not evidence/ — this is a
  reusable artifact, checked into the repo like any other code)
- evidence/load-test-engineer.json — what the script tests, and a
  pointer to the script's path

## Gate condition
The script parses and runs under `k6 run --vus 1 --iterations 1` (or an
equivalent one-shot dry run) without error, before it's considered done
— a script that only "looks right" but has never executed is not this
agent's finished output.

## Prohibited
Never targets anything but `knowledge/api/`'s documented endpoints and
`http://localhost` — see the ShopFlow-pattern safety rule this system
inherits: local training/dev only, never a shared or production target.

## On missing evidence
If `risk-workload.json`'s targets are placeholders (flagged per that
agent's gate), this script's header comment states that explicitly —
"this test validates against an unvalidated placeholder target," so
nobody downstream mistakes a placeholder-based pass for a real SLO pass.
