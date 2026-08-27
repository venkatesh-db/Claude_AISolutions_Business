# RxFlow Production Prompts — Simple / Intermediate / Advanced

Three tiered, copy-paste-ready prompts. Each builds a real, runnable slice of
the RxFlow production stack **and** forces a required "concept proof" for
every mechanism it introduces — a contrast experiment that shows why the
alternative mechanism would have failed, not just a usage example.

## Reference: the stack

| Layer | Technology |
|---|---|
| API | FastAPI, Pydantic v2 |
| Domain | Plain Python service layer |
| Data | PostgreSQL, SQLAlchemy 2.x, Alembic |
| Cache and locks | Redis |
| Async work | Celery workers |
| Events | Kafka (Redpanda locally) |
| Analytics | pandas / Polars ETL |
| Testing | pytest, pytest-asyncio, hypothesis, testcontainers, locust |
| Quality gates | ruff, mypy --strict, bandit, pip-audit |
| Ops | Docker Compose, GitHub Actions, OpenTelemetry |

## Reference: the mechanism table

| What you need | What you should build |
|---|---|
| A one-time constraint | A prompt |
| A standing repository standard | CLAUDE.md |
| Something you type most days | A custom slash command |
| A repeatable multi-step workflow with judgement in it | A Skill |
| A rule that must fire whether or not anyone remembers | A hook |
| Access to a system outside the repo | An MCP server |
| A bounded investigation you want done in isolation | A sub-agent |
| Something that must run with no human present | Headless / CI |

---

## Simple (2–4 yrs) — CRUD service + four foundational mechanisms

**Mechanisms introduced:** prompt, CLAUDE.md, slash command, hook.

```
Build a minimal RxFlow order-pricing service in Python: FastAPI + Pydantic v2
for the API, plain Python service functions for domain logic, PostgreSQL via
SQLAlchemy 2.x (async engine) with Alembic migrations. One resource: orders
(id, lens_type, surcharges[], total_price, status).

Build:
1. A root CLAUDE.md with verified `docker compose up -d db && alembic upgrade
   head && pytest -q` and `ruff check . && mypy --strict src/` commands (run
   them yourself, paste real output), plus the non-negotiable: every Alembic
   revision needs a working downgrade().
2. A .claude/commands/test.md slash command that runs the full verify loop
   in one shot.
3. Two hooks in .claude/settings.json: a PostToolUse hook running ruff+mypy
   on every edited .py file, AND a PreToolUse hook that blocks `git push
   --force` outright.
4. docker-compose.yml with Postgres. Implement POST /orders, GET
   /orders/{id}, PATCH /orders/{id}/status, with pytest tests against a real
   Postgres via testcontainers.

CONCEPT PROOFS — do not skip these, they are the point of the exercise:

- PROMPT vs CLAUDE.md: ask me, as a one-off, "what does SQLAlchemy's
  `selectinload` do and should I use it here?" Answer it, then don't save
  it anywhere. Separately, add the Alembic-downgrade rule to CLAUDE.md. Then
  explicitly tell me: which of these two answers will still apply the next
  time someone opens a fresh session on this repo, and which one is already
  gone? That's the whole difference between a prompt and CLAUDE.md.

- HOOK vs prose rule: first, try to run `git push --force` for real and show
  me it gets blocked (exit code, stderr from the hook). Then add a sentence
  to CLAUDE.md instead: "never force-push." Try the force-push again with
  ONLY the CLAUDE.md sentence in place (hook temporarily disabled) and show
  me that nothing stops you — CLAUDE.md is a rule an agent can still forget
  to follow under pressure; a hook structurally cannot be skipped. Re-enable
  the hook when done.
```

---

## Intermediate (4–6 yrs) — adds Skill + headless CI

**Mechanisms introduced:** Skill, headless/CI. (Builds on Simple tier.)

```
Extend the Simple-tier RxFlow service with:

1. Redis: a read-through cache on GET /orders/{id} (TTL 30s) and a
   distributed lock around the surcharge-calculation critical section.
2. A Celery worker (Redis broker) that recalculates pricing asynchronously
   on a new surcharge rule — idempotent under retry (same order_id +
   rule_version = no-op).
3. A Skill at .claude/skills/release-readiness/SKILL.md: finds services
   changed since the last git tag, runs only affected tests, diffs the
   OpenAPI schema against the previous tag, checks new Alembic revisions
   have a downgrade(), emits a GO/NO-GO report.
4. GitHub Actions CI (.github/workflows/ci.yml): Postgres + Redis as
   services, runs ruff + mypy --strict + pytest, fails the build on red.

CONCEPT PROOFS:

- SLASH COMMAND vs SKILL: try to make /test conditionally skip Celery tests
  when only the API changed, and conditionally add an OpenAPI diff when the
  API changed. Notice you're now writing branching logic into a "command" —
  stop, and tell me explicitly why this belongs in the Skill instead (a
  command runs the same fixed steps every time; the moment it needs to
  decide what to do based on what changed, it's a Skill).

- SKILL judgment, proven not asserted: run release-readiness against two
  different diffs I'll hand you — one that only touches the Celery worker,
  one that only touches the API schema. Show me, side by side, that the
  Skill's actual checklist output differs between the two (it should run
  the OpenAPI diff only for the second, not both times identically). If it
  runs the same steps regardless of the diff, it isn't actually exercising
  judgment — go fix it until it does.

- HEADLESS / CI, proven unattended: push a commit that breaks a test, then
  STOP interacting with me entirely — don't ask me to check anything. Tell
  me the exact time you pushed. I will independently check the Actions tab
  later and report back the run's timestamp and result, so we confirm it
  ran and failed with nobody watching it in real time.
```

---

## Advanced (6–9 yrs) — adds MCP server + sub-agent

**Mechanisms introduced:** MCP server, sub-agent. (Builds on Simple + Intermediate tiers.)

```
Extend the RxFlow service (Simple + Intermediate tiers) with:

1. Kafka (Redpanda locally) — publish OrderPriced on every successful
   pricing calc; a replay-safe consumer group in a separate worker.
2. A pandas/Polars ETL job producing a daily revenue-by-lens-type parquet
   report, correct on empty and 1M-row synthetic datasets.
3. hypothesis property tests for surcharge stacking (invariant: total always
   equals the sum of individual surcharges, under any ordering) and a
   locust load test at 50 rps / 60s with a p99 assertion.
4. bandit + pip-audit in CI, blocking on HIGH+.
5. OpenTelemetry tracing across FastAPI → Celery → Kafka — one trace ID
   visible end-to-end for a single order.
6. An MCP server (rxflow_mcp pattern: get_ticket, search_incidents,
   get_runbook, create_change_request→pending_approval,
   update_ticket_status requiring verified_by_tests=True).

CONCEPT PROOFS:

- MCP SERVER vs "just call the API from a hook/Skill": before building the
  MCP server, try to get the ticket data into this session by having a hook
  or the Skill curl the ticketing API directly and dump the result into a
  file the agent reads. Notice this has no typed contract, no read/write
  distinction, no approval gate — any code path could "accidentally" call
  a write endpoint. Now build the real MCP server with
  create_change_request always landing on pending_approval, and show me
  the same ticket-fetch-then-fix flow through it, where a write is
  structurally impossible without the pending_approval step. That contrast
  is why this needed a typed, governed server and not an ad hoc curl call.

- SUB-AGENT vs asking inline: first, review a diff's security implications
  yourself, inline, in this same conversation — note how much context that
  consumed (rough token/turn count). Then launch a read-only sub-agent to
  redo the identical review in isolation, returning only a verdict with
  file:line evidence. Show me the sub-agent's full investigation never
  entered this conversation's context — only its final verdict did. That's
  the entire benefit: the digging is isolated, only the answer comes back.

Run the full loop once end-to-end: introduce a real concurrency bug (double
surcharge under concurrent Celery retries), let the hypothesis test catch
it, fix it, get the sub-agent's isolated sign-off, push, and show CI going
green with a trace ID that follows the one order through every layer.
```

---

## Why this structure

Each tier forces a **contrast experiment**, not just an add: prompt-vs-CLAUDE.md
(what persists), hook-vs-prose (what's structural), command-vs-Skill (what
needs judgment), CI-vs-watched (what runs unattended), MCP-vs-adhoc-call
(what's governed), sub-agent-vs-inline (what's isolated). Building the stack
alone teaches FastAPI/Celery/Kafka; it does not by itself teach *why* each of
the eight mechanisms exists instead of one of the others — the concept proofs
are what closes that gap.
