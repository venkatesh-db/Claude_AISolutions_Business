
Role: you are acting as principal architect for a corporate training
lab, not as the participants. Build RxFlow, a Python teaching
repository. This is a training artefact, not a product. Every design
choice serves the lab exercise described at the end.

DOMAIN
Prescription-to-lens order and lab routing. An optician submits a
prescription and frame choice. The system validates the prescription
against what a lens can physically be ground to, prices it, routes the
job to an Rx lab by capability and live load, schedules surfacing and
coating, and tracks to shipment.

STACK
FastAPI + Pydantic v2 · plain Python service layer · PostgreSQL with
SQLAlchemy 2.x and Alembic · Redis for cache and locks · Celery workers ·
Kafka via Redpanda · pytest, pytest-asyncio, hypothesis, testcontainers ·
ruff, mypy --strict, bandit, pip-audit · Docker Compose · OpenTelemetry.

WHAT LAB 1 WILL ASK PARTICIPANTS TO ESTABLISH
Build the repo so each of these has a real, findable answer:

  1. Module map and service boundaries — at least 5 modules with genuine
     boundaries, and at least one boundary that is violated somewhere.
  2. Full request path for POST /orders — route → schema → service →
     repository → worker → event. Deep enough that tracing it takes
     effort, shallow enough to finish in 90 minutes.
  3. Build, test, lint, type-check commands — these must ACTUALLY RUN.
     Include at least one command in the README that is stale and fails,
     so "verified by running" differs from "inferred from docs".
  4. Schema and migration state — Alembic with 4-6 revisions, one of
     which has no downgrade().
  5. Redis and Celery usage — Redis used as both cache and lock, with an
     in-flight counter updated by read-modify-write, not atomically.
     Celery with a retry policy that amplifies load on timeout.
  6. Outbound calls and timeouts — 3-4 external calls. At least one with
     no timeout set at all. At least one with a retry policy that
     compounds with a caller's retry.
  7. Auth and authorization model — token auth on most routes, and one
     endpoint (lab override) with no authorization check.
  8. Where PII reaches the logs — prescription values and patient
     identifiers emitted in at least two places, one obvious in a log
     call, one indirect via a model dump or object repr.
  9. Five highest-risk files — make risk genuinely uneven: one large
     untested module (pricing, ~900 lines, three copies of the discount
     rule), one concurrency-sensitive module, one with raw SQL.
 10. Unknowns — leave 2-3 things genuinely undeterminable from the code
     alone (e.g. which layer owns retry responsibility), so an honest
     report has to say "cannot determine".

SEEDED DEFECTS
Ten, surfacing across the week. Participants are not told what they are:
  1. Duplicate lens job on retry of a slow submit — no idempotency
  2. Prescription validation silently clamps out-of-range cylinder/axis
  3. Lab routing selects by static priority, ignores live capacity
  4. Celery retry amplifies load ~3x on connector timeout
  5. Redis in-flight counter drifts under concurrency
  6. Patient identifiers and prescriptions in application logs
  7. Lab-override endpoint has no authorization check
  8. 900-line pricing module, no tests, three copies of the discount rule
  9. Alembic revision with no downgrade path
 10. Ad-hoc reporting query built with f-strings — SQL injection

DESIGN RULES
- The test suite must PASS while all ten defects are live. For each
  defect, tell me which test looks like it should have caught it and
  why it does not.
- Concurrency defects need realistic work inside the window — a pricing
  call, an external request. Never a sleep().
- No comment anywhere hints that code is intentionally wrong. No TODO,
  no "note: race here". The code must read as ordinary work under
  deadline.
- Each defect must be either reproducible on demand or demonstrable
  with a one-line command.
- Realistic mess: inconsistent naming across modules, one dead module,
  one abandoned refactor half-applied. Undocumented does not mean clean.
- README must be plausible and partly wrong — the kind a team writes
  once and stops updating.

DELIVERABLES — three separate outputs, do not mix them

1. THE PARTICIPANT REPOSITORY
   The codebase itself. No hints, no answer keys, no diagrams. This is
   what Day 1 hands to the room.

2. INSTRUCTOR.md  (not part of the participant repo)
   For each of the 10 defects:
     - file and line range
     - the one-line reproduction or demonstration command
     - expected output when it fires
     - which existing test looks like it should catch it, and why it
       does not

3. INSTRUCTOR-DIAGRAMS.md  (not part of the participant repo)
   Exactly two diagrams, as Mermaid:
     a. SYSTEM DESIGN — one diagram, the whole repo: modules, data
        stores, external calls, boundaries. Mark the violated boundary.
     b. CODE FLOW — one diagram, tracing POST /orders end to end,
        route through to the Kafka event. Mark every point where a
        defect from the list above sits on this path.
   Do NOT produce a diagram per defect. Ten diagrams for ten defects
   defeats the lab — participants are supposed to produce their own
   trace of each defect as part of the graded exercise. Two diagrams,
   both annotated, is correct and sufficient for instructor prep.

ACCEPTANCE — do not present anything until all hold
- docker compose up brings the stack up on a clean machine
- pytest passes with all ten defects live
- ruff and mypy --strict pass
- each reproduction command in INSTRUCTOR.md fails on 3 consecutive
  runs, output pasted
- POST /orders works end to end against the running stack
- both diagrams in INSTRUCTOR-DIAGRAMS.md render as valid Mermaid and
  each annotation points at a real file:line
- you paste the actual output of every command above, not a summary

Iterate until acceptance is met. Do not ask me between attempts.
Report at the end: what failed on the way, and what you changed.