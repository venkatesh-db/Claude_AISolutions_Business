# ADR 0001: Initialize app.state at creation time, not via a lifespan hook

**Status:** Accepted
**Context source:** real bug hit while building `taskflow-ops`, not hypothetical

## Context

`taskflow_ops.main`'s original implementation initialized `app.state.store`
and `app.state.request_count` inside a FastAPI `lifespan` async context
manager, which is the documented pattern for resources needing async
setup/teardown.

## The problem, found by running tests, not by review

`httpx.ASGITransport` (used by the test suite to call the app in-process)
does not trigger ASGI lifespan events by default. Every test failed with
`AttributeError: 'State' object has no attribute 'request_count'` —
`app.state` was never populated in the test environment, even though the
same code worked correctly when run behind `uvicorn`, which does drive
lifespan events.

## Decision

State that doesn't need async setup (no DB connection pool, no external
client handshake) is initialized directly at module load time, on `app`
right after its construction — not inside `lifespan`.

## Consequences

- Simpler: no dependency on the ASGI server actually driving lifespan
  events, which varies between `uvicorn` (does) and `httpx.ASGITransport`
  (doesn't, by default).
- If `taskflow-ops` later adds a resource that genuinely needs async
  setup (a database pool, for example), `lifespan` should be reintroduced
  **for that resource specifically** — this ADR does not forbid
  `lifespan`, it forbids using it for state that doesn't need it.
- Test coverage exists for this exact failure mode:
  `tests/test_api.py` exercises every route through `ASGITransport`,
  which is what caught the original bug.
