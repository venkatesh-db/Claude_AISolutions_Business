# Test fixtures actually used against taskflow-ops

Pulled directly from `taskflow-ops/tests/test_api.py` — these are the
real payloads the test suite exercises, not illustrative examples.

## Valid task creation

```json
POST /tasks
{"name": "grind-lens"}
```
Expected: `201`, `status: "queued"`, a fresh `task_id`.

## Unknown task lookup

```
GET /tasks/does-not-exist
```
Expected: `404`.

## Concurrency probe (used by `tools/concurrency_check.py`)

N concurrent `POST /tasks` with distinct `name` values
(`concurrent-task-0` .. `concurrent-task-{N-1}`); expect N distinct
`task_id`s and `/metrics`'s `tasks_by_status.queued` ≥ N afterward.

## What's missing

No fixture exists yet for the `advance` endpoint's failure modes (e.g.
advancing an unknown task, or an invalid status value) — `product/`'s
lifecycle note flags that `advance` doesn't enforce transition order, so
a fixture asserting that non-enforcement (not just the happy path) would
close a real coverage gap.
