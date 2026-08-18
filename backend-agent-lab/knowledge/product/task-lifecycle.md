# Product rule: task lifecycle

**Source:** `taskflow-ops/src/taskflow_ops/domain.py` — `TaskStatus`,
directly, not paraphrased from a separate doc that could drift from it.

## States

`queued` → `running` → `done` | `failed`

## Rules, as actually enforced by the code

- A task starts in `queued` on creation (`TaskStore.create`) — there is
  no way to create a task in any other state.
- `TaskStore.advance(task_id, status)` allows transition to **any**
  status from **any** status — there is currently no state-machine
  enforcement (e.g. nothing stops `queued` → `done` directly, skipping
  `running`, or `done` → `queued`). This is either a real business rule
  gap or an intentional simplification for this reference service — not
  yet decided, flagged here rather than assumed.
- `task_id` is a `uuid4().hex`, generated server-side; a client never
  supplies one.

## What this means for testing

Any test asserting "a task cannot skip `running`" will fail against the
current implementation — that's not a test bug, it's the code not
enforcing a rule this document doesn't actually claim exists. If that
rule is wanted, it belongs in `TaskStore.advance`, not just in a test.
